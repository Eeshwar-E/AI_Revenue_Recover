from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.case import RevenueRiskCase
from app.models.customer import Customer
from app.models.recovery import RecoveryAction
from app.models.audit import AuditEvent
from app.agent.orchestrator import RecoveryOrchestrator
from app.schemas.case import CaseResponse, CaseDetail
from typing import List, Optional

router = APIRouter(prefix="/api/cases", tags=["cases"])


def _mask_email(e: str | None) -> str | None:
    if not e or "@" not in e:
        return e
    u, d = e.split("@", 1)
    return f"{u[:2]}***@{d}"


def _mask_phone(p: str | None) -> str | None:
    if not p or len(p) < 4:
        return "****"
    return f"****{p[-4:]}"


@router.get("", response_model=List[CaseResponse])
def get_cases(status: Optional[str] = None, source_type: Optional[str] = None, risk_level: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RevenueRiskCase)
    if status:
        query = query.filter(RevenueRiskCase.status == status)
    if source_type:
        query = query.filter(RevenueRiskCase.source_type == source_type)
    if risk_level:
        query = query.filter(RevenueRiskCase.risk_level == risk_level)
    cases = query.order_by(RevenueRiskCase.id.desc()).all()
    result = []
    for case in cases:
        customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
        case_dict = {
            "id": case.id, "case_number": case.case_number,
            "customer_id": case.customer_id,
            "customer_name": customer.name if customer else "Unknown",
            "source_type": case.source_type, "amount_at_risk": case.amount_at_risk,
            "recovered_amount": case.recovered_amount, "status": case.status,
            "risk_level": case.risk_level, "risk_score": case.risk_score,
            "root_cause": case.root_cause, "root_cause_detail": case.root_cause_detail,
            "current_retry_count": case.current_retry_count,
            "max_retries": case.max_retries,
            "recommended_action": case.recommended_action,
            "action_reasoning": case.action_reasoning,
            "confidence": case.confidence, "should_escalate": case.should_escalate,
            "stop_reason": case.stop_reason, "last_action_at": case.last_action_at,
            "next_action_at": case.next_action_at, "created_at": case.created_at,
        }
        result.append(case_dict)

    return result


@router.get("/{case_id}")
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    actions = db.query(RecoveryAction).filter(RecoveryAction.case_id == case.id).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.case_id == case.id).order_by(AuditEvent.id).all()
    return {
        "id": case.id, "case_number": case.case_number,
        "customer_id": case.customer_id,
        "customer_name": customer.name if customer else "Unknown",
        "customer_email": _mask_email(customer.email) if customer else None,
        "customer_phone": _mask_phone(customer.phone) if customer else None,
        "customer_segment": customer.segment if customer else None,
        "customer_lifetime_value": customer.lifetime_value if customer else 0,
        "historical_success_rate": customer.historical_success_rate if customer else 0,
        "recent_success_rate": customer.recent_success_rate if customer else 0,
        "source_type": case.source_type,
        "amount_at_risk": case.amount_at_risk,
        "recovered_amount": case.recovered_amount,
        "status": case.status, "risk_level": case.risk_level,
        "risk_score": case.risk_score, "root_cause": case.root_cause,
        "current_retry_count": case.current_retry_count,
        "max_retries": case.max_retries,
        "recommended_action": case.recommended_action,
        "action_reasoning": case.action_reasoning,
        "confidence": case.confidence,
        "should_escalate": case.should_escalate,
        "stop_reason": case.stop_reason,
        "last_action_at": case.last_action_at,
        "actions": [
            {"id": a.id, "action_type": a.action_type, "status": a.status,
             "reason": a.reason, "recovered_amount": a.recovered_amount}
            for a in actions
        ],
        "audit_events": [
            {"id": e.id, "event_type": e.event_type,
             "risk_score": e.risk_score, "recommended_action": e.recommended_action,
             "policy_result": e.policy_result, "actual_action": e.actual_action,
             "action_result": e.action_result, "recovery_amount": e.recovery_amount,
             "details": e.details, "timestamp": str(e.timestamp) if e.timestamp else None}
            for e in audit_events
        ],
    }


@router.post("/{case_id}/run")
def run_case(case_id: int, db: Session = Depends(get_db)):
    orchestrator = RecoveryOrchestrator(db)
    result = orchestrator.run_case(case_id)
    return result


@router.post("/{case_id}/approve")
def approve_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "ACTION_PENDING"
    audit = AuditEvent(case_id=case.id, actor="HUMAN", event_type="MANUAL_APPROVAL",
                       details="Human approved the case for autonomous execution")
    db.add(audit)
    db.commit()
    orchestrator = RecoveryOrchestrator(db)
    result = orchestrator.run_case(case_id)
    return result


@router.post("/{case_id}/reject")
def reject_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "STOPPED"
    case.stop_reason = "Rejected by operator"
    db.add(AuditEvent(case_id=case.id, actor="HUMAN", event_type="MANUAL_REJECT",
                      details="Operator rejected autonomous action"))
    db.commit()
    return {"status": "stopped", "case_id": case.id}


@router.post("/{case_id}/escalate")
def escalate_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "ESCALATED"
    case.should_escalate = 1
    db.add(AuditEvent(case_id=case.id, actor="HUMAN", event_type="MANUAL_ESCALATE",
                      details="Operator escalated case"))
    db.commit()
    return {"status": "escalated", "case_id": case.id}


@router.post("/{case_id}/stop")
def stop_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "STOPPED"
    case.stop_reason = "Manually stopped by operator"
    audit = AuditEvent(case_id=case.id, actor="HUMAN", event_type="MANUAL_STOP",
                       details="Case manually stopped by operator")
    db.add(audit)
    db.commit()
    return {"status": "stopped", "case_id": case.id}


@router.post("/{case_id}/retry")
def retry_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.status == "RECOVERED":
        raise HTTPException(status_code=400, detail="Case already recovered")
    case.status = "RETRY_PENDING"
    db.commit()
    orchestrator = RecoveryOrchestrator(db)
    result = orchestrator.run_case(case_id)
    return result