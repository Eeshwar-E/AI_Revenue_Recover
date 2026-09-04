from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.agent.tools import ToolRegistry
from app.models.case import RevenueRiskCase
from app.agent.orchestrator import RecoveryOrchestrator

router = APIRouter(prefix="/api/agent", tags=["agent"])

tool_registry = ToolRegistry()


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