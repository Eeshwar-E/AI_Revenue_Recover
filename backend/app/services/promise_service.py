"""Promise-to-pay tracker + mandate retry sequencer (§3F, §3E)."""
from sqlalchemy.orm import Session
from app.models.promise import PromiseToPay
from app.models.invoice import Invoice
from app.models.case import RevenueRiskCase
from app.models.audit import AuditEvent
from datetime import datetime
from typing import Dict, Any

MANDATE_WAIT_HOURS = {
    "network_error": 2,
    "insufficient_funds": 48,
    "bank_decline": 24,
    "expired_card": 0,  # request update, no auto retry
    "invalid_payment_method": 0,
    "fraud_risk_block": 0,
}


class PromiseService:
    def __init__(self, db: Session):
        self.db = db

    def check_promises(self) -> Dict[str, Any]:
        now = datetime.now()
        overdue = self.db.query(PromiseToPay).filter(
            PromiseToPay.status == "PENDING", PromiseToPay.promise_date < now).all()
        escalated = 0
        for p in overdue:
            p.missed_count = (p.missed_count or 0) + 1
            if p.missed_count >= 2:
                p.status = "MISSED"
                escalated += 1
                self.db.add(AuditEvent(actor="AGENT", event_type="PROMISE_MISSED",
                                       details=f"Promise {p.id} missed {p.missed_count}x",
                                       timestamp=now))
            else:
                p.status = "OVERDUE"
        self.db.commit()
        return {"checked": len(overdue), "escalated": escalated}

    def mandate_next_step(self, failure_reason: str, attempt: int) -> Dict[str, Any]:
        wait = MANDATE_WAIT_HOURS.get(failure_reason, 24)
        if wait == 0:
            return {"action": "UPDATE_PAYMENT_METHOD", "wait_hours": 0, "stop": False}
        if attempt >= 3:
            return {"action": "ESCALATE", "wait_hours": 0, "stop": True}
        return {"action": "RETRY_PAYMENT", "wait_hours": wait, "stop": False}
