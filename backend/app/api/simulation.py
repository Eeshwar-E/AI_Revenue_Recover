from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, init_db, engine
from app.models import Base
from app.seed.seed_data import SeedData

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed = SeedData(db)
    stats = seed.seed_all()
    return {"message": "Database seeded successfully", "stats": stats}


@router.post("/run")
def run_simulation(db: Session = Depends(get_db)):
    from app.services.batch_service import BatchService
    bs = BatchService(db)
    result = bs.run_full_batch()
    return result


@router.post("/demo/reset")
def demo_reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed = SeedData(db)
    stats = seed.seed_all()
    return {"message": "Demo reset complete", "stats": stats}


@router.post("/demo/run")
def demo_run(db: Session = Depends(get_db)):
    from app.services.batch_service import BatchService
    bs = BatchService(db)
    result = bs.run_full_batch()
    from app.models.audit import AuditEvent
    audit = AuditEvent(actor="SYSTEM", event_type="DEMO_RUN",
                       batch_id=result["batch_id"], recovery_amount=result["recovered_amount"],
                       details=f"Demo: {result['cases_processed']} cases, ₹{result['recovered_amount']:,.0f} recovered ({result['recovery_rate']}%)")
    db.add(audit)
    db.commit()
    return result