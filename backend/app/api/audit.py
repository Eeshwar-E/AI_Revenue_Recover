from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditEvent

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/{case_id}")
def get_audit_trail(case_id: int, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(AuditEvent.case_id == case_id).order_by(AuditEvent.id).all()
    return [
        {"id": e.id, "case_id": e.case_id, "actor": e.actor, "event_type": e.event_type,
         "risk_score": e.risk_score, "root_cause": e.root_cause,
         "recommended_action": e.recommended_action, "policy_result": e.policy_result,
         "actual_action": e.actual_action, "action_result": e.action_result,
         "recovery_amount": e.recovery_amount, "next_step": e.next_step,
         "stop_reason": e.stop_reason, "details": e.details,
         "timestamp": str(e.timestamp) if e.timestamp else None}
        for e in events
    ]


@router.get("")
def get_all_audit_events(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    from app.models.audit import AuditEvent
    total = db.query(AuditEvent).count()
    events = db.query(AuditEvent).order_by(AuditEvent.id.desc()).offset(offset).limit(limit).all()
    return {"events": [
        {"id": e.id, "case_id": e.case_id, "actor": e.actor, "event_type": e.event_type,
         "actual_action": e.actual_action, "action_result": e.action_result,
         "recovery_amount": e.recovery_amount, "details": e.details,
         "timestamp": str(e.timestamp) if e.timestamp else None}
        for e in events], "total": total}