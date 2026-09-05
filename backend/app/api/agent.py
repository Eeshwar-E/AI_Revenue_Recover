from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.agent.tools import ToolRegistry
from app.models.case import RevenueRiskCase
from app.agent.orchestrator import RecoveryOrchestrator

router = APIRouter(prefix="/api/agent", tags=["agent"])

tool_registry = ToolRegistry()
tool_registry.register("get_payment_status", lambda transaction_id: {"status": "CHECKED", "transaction_id": transaction_id})
tool_registry.register("retry_payment", lambda transaction_id: {"status": "QUEUED", "transaction_id": transaction_id})
tool_registry.register("send_notification", lambda customer_id, channel="SMS", message="": {"status": "QUEUED", "customer_id": customer_id, "channel": channel})
tool_registry.register("create_escalation", lambda case_id, reason="", priority="MEDIUM": {"status": "ESCALATED", "case_id": case_id, "reason": reason})
tool_registry.register("check_policy", lambda action_type, case_id: {"result": "APPROVED", "action_type": action_type})


@router.post("/analyze/{case_id}")
def analyze_case(case_id: int, db: Session = Depends(get_db)):
    from app.models.customer import Customer
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        return {"error": "Case not found"}
    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    if not customer:
        return {"error": "Customer not found"}
    from app.agent.decision_engine import DecisionEngine
    decision_engine = DecisionEngine(use_llm=False, api_key=None)
    case_data = {
        "customer_id": customer.id,
        "customer_name": customer.name,
        "amount": case.amount_at_risk,
        "source_type": case.source_type,
        "failure_reason": case.root_cause or "unknown",
        "historical_success_rate": customer.historical_success_rate,
        "recent_success_rate": customer.recent_success_rate,
        "retry_count": case.current_retry_count,
    }
    decision = decision_engine.analyze_case(case_data)
    case.risk_score = decision["risk_score"]
    case.risk_level = decision["risk_level"]
    case.confidence = decision["confidence"]
    case.recommended_action = decision["recommended_action"]
    case.action_reasoning = decision["reasoning"]
    from app.models.audit import AuditEvent
    audit = AuditEvent(case_id=case.id, actor="AGENT", event_type="ANALYSIS",
                       risk_score=decision["risk_score"], root_cause=decision["root_cause"],
                       recommended_action=decision["recommended_action"], details=decision["reasoning"])
    db.add(audit)
    db.commit()
    return decision


@router.post("/run/{case_id}")
def run_agent(case_id: int, db: Session = Depends(get_db)):
    orchestrator = RecoveryOrchestrator(db)
    result = orchestrator.run_case(case_id)
    return result


@router.get("/decisions/{case_id}")
def get_decisions(case_id: int, db: Session = Depends(get_db)):
    from app.models.audit import AuditEvent
    events = db.query(AuditEvent).filter(
        AuditEvent.case_id == case_id, AuditEvent.event_type == "ANALYSIS"
    ).order_by(AuditEvent.id.desc()).all()
    return [
        {"id": e.id, "risk_score": e.risk_score, "root_cause": e.root_cause,
         "recommended_action": e.recommended_action, "details": e.details,
         "timestamp": str(e.timestamp) if e.timestamp else None}
        for e in events
    ]


@router.get("/tools")
def list_tools():
    return {"tools": tool_registry.list_tools()}


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    """Observability: agent runs with run_id/duration/steps/result (§29)."""
    from app.models.agent_run import AgentRun
    runs = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(100).all()
    return [
        {"run_id": r.run_id, "case_id": r.case_id, "batch_id": r.batch_id,
         "start_time": str(r.start_time) if r.start_time else None,
         "end_time": str(r.end_time) if r.end_time else None,
         "duration_seconds": r.duration_seconds, "steps_executed": r.steps_executed,
         "decision": r.decision, "actions": r.actions, "result": r.result,
         "revenue_recovered": r.revenue_recovered, "failure_reason": r.failure_reason}
        for r in runs
    ]