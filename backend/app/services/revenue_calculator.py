from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.case import RevenueRiskCase
from app.models.recovery import RecoveryAction
from typing import Dict, Any


class RevenueCalculator:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_summary(self) -> Dict[str, Any]:
        total_at_risk = self.db.query(func.sum(RevenueRiskCase.amount_at_risk)).filter(
            RevenueRiskCase.status.notin_(["RECOVERED", "STOPPED", "FAILED"])
        ).scalar() or 0
        total_recovered = self.db.query(func.sum(RevenueRiskCase.recovered_amount)).filter(
            RevenueRiskCase.recovered_amount > 0
        ).scalar() or 0
        total_at_risk_all = self.db.query(func.sum(RevenueRiskCase.amount_at_risk)).scalar() or 0
        total_cases = self.db.query(func.count(RevenueRiskCase.id)).scalar() or 0
        active_cases = self.db.query(func.count(RevenueRiskCase.id)).filter(
            RevenueRiskCase.status.notin_(["RECOVERED", "STOPPED", "FAILED"])
        ).scalar() or 0
        recovered_cases = self.db.query(func.count(RevenueRiskCase.id)).filter(
            RevenueRiskCase.status == "RECOVERED"
        ).scalar() or 0
        escalated_cases = self.db.query(func.count(RevenueRiskCase.id)).filter(
            RevenueRiskCase.status == "ESCALATED"
        ).scalar() or 0
        failed_cases = self.db.query(func.count(RevenueRiskCase.id)).filter(
            RevenueRiskCase.status.in_(["STOPPED", "FAILED"])
        ).scalar() or 0
        recovery_rate = (total_recovered / max(total_at_risk_all, 1)) * 100
        return {
            "total_revenue_at_risk": round(total_at_risk_all, 2),
            "total_revenue_recovered": round(total_recovered, 2),
            "active_revenue_at_risk": round(total_at_risk, 2),
            "recovery_rate": round(recovery_rate, 1),
            "total_cases": total_cases,
            "active_cases": active_cases,
            "recovered_cases": recovered_cases,
            "escalated_cases": escalated_cases,
            "failed_cases": failed_cases,
        }

    def get_recovery_by_type(self) -> list:
        rows = self.db.query(
            RevenueRiskCase.source_type,
            func.sum(RevenueRiskCase.recovered_amount).label("recovered"),
            func.sum(RevenueRiskCase.amount_at_risk).label("at_risk"),
            func.count(RevenueRiskCase.id).label("count")
        ).group_by(RevenueRiskCase.source_type).all()
        return [
            {"type": r.source_type, "recovered": round(r.recovered or 0, 2), "at_risk": round(r.at_risk or 0, 2), "count": r.count}
            for r in rows
        ]

    def get_recovery_by_action(self) -> list:
        rows = self.db.query(
            RecoveryAction.action_type,
            func.sum(RecoveryAction.recovered_amount).label("recovered"),
            func.count(RecoveryAction.id).label("count")
        ).filter(RecoveryAction.recovered_amount > 0).group_by(RecoveryAction.action_type).all()
        return [{"action_type": r.action_type, "recovered": round(r.recovered or 0, 2), "count": r.count} for r in rows]

    def get_risk_distribution(self) -> list:
        rows = self.db.query(
            RevenueRiskCase.risk_level,
            func.count(RevenueRiskCase.id).label("count"),
            func.sum(RevenueRiskCase.amount_at_risk).label("amount")
        ).group_by(RevenueRiskCase.risk_level).all()
        return [{"risk_level": r.risk_level, "count": r.count, "amount": round(r.amount or 0, 2)} for r in rows]

    def get_recovery_funnel(self) -> list:
        total = self.db.query(func.count(RevenueRiskCase.id)).scalar() or 0
        diagnosed = self.db.query(func.count(RevenueRiskCase.id)).filter(RevenueRiskCase.status.notin_(["DETECTED"])).scalar() or 0
        with_strategy = self.db.query(func.count(RevenueRiskCase.id)).filter(RevenueRiskCase.recommended_action.isnot(None)).scalar() or 0
        with_action = self.db.query(func.count(RevenueRiskCase.id)).filter(
            RevenueRiskCase.status.in_(["ACTION_EXECUTED", "RETRY_PENDING", "RECOVERED", "ESCALATED", "STOPPED"])
        ).scalar() or 0
        recovered = self.db.query(func.count(RevenueRiskCase.id)).filter(RevenueRiskCase.status == "RECOVERED").scalar() or 0
        return [
            {"stage": "Detected", "count": total},
            {"stage": "Diagnosed", "count": diagnosed},
            {"stage": "Strategy Selected", "count": with_strategy},
            {"stage": "Action Executed", "count": with_action},
            {"stage": "Recovered", "count": recovered},
        ]

    def get_failure_reasons(self) -> list:
        from app.models.transaction import Transaction
        rows = self.db.query(
            Transaction.failure_reason,
            func.count(Transaction.id).label("count")
        ).filter(Transaction.status == "FAILED", Transaction.failure_reason.isnot(None)).group_by(Transaction.failure_reason).all()
        return [{"reason": r.failure_reason, "count": r.count} for r in rows]