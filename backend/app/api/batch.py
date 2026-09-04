from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.batch_service import BatchService

router = APIRouter(prefix="/api/batch", tags=["batch"])


@router.post("/analyze")
def analyze_batch(db: Session = Depends(get_db)):
    bs = BatchService(db)
    risks = bs.risk_engine.scan_all_customers()
    return {"risks_found": len(risks), "risks": risks}


@router.post("/run")
def run_batch(db: Session = Depends(get_db)):
    bs = BatchService(db)
    result = bs.run_full_batch()
    from app.models.audit import AuditEvent
    audit = AuditEvent(actor="SYSTEM", event_type="BATCH_RUN",
                       batch_id=result["batch_id"], recovery_amount=result["recovered_amount"],
                       details=f"Batch {result['batch_id']}: {result['cases_processed']} cases, ₹{result['recovered_amount']:,.0f} recovered, {result['recovery_rate']}%")
    db.add(audit)
    db.commit()
    return result


@router.get("/{batch_id}")
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    from app.models.audit import AuditEvent
    audit = db.query(AuditEvent).filter(AuditEvent.batch_id == batch_id).first()
    if not audit:
        return {"error": "Batch not found"}
    return {"batch_id": batch_id, "details": audit.details,
            "recovery_amount": audit.recovery_amount,
            "timestamp": str(audit.timestamp) if audit.timestamp else None}