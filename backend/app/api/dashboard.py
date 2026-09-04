from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.revenue_calculator import RevenueCalculator

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    calc = RevenueCalculator(db)
    return calc.get_dashboard_summary()


@router.get("/recovery")
def get_recovery_by_type(db: Session = Depends(get_db)):
    calc = RevenueCalculator(db)
    return calc.get_recovery_by_type()


@router.get("/recovery/by-action")
def get_recovery_by_action(db: Session = Depends(get_db)):
    calc = RevenueCalculator(db)
    return calc.get_recovery_by_action()


@router.get("/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    calc = RevenueCalculator(db)
    return calc.get_risk_distribution()


@router.get("/funnel")
def get_funnel(db: Session = Depends(get_db)):
    calc = RevenueCalculator(db)
    return calc.get_recovery_funnel()


@router.get("/failure-reasons")
def get_failure_reasons(db: Session = Depends(get_db)):
    calc = RevenueCalculator(db)
    return calc.get_failure_reasons()