from typing import Dict, Any
from app.config import settings


class PolicyEngine:
    def __init__(self):
        self.MAX_RETRIES = settings.MAX_RETRIES
        self.MAX_CONTACTS_PER_WEEK = settings.MAX_CONTACTS_PER_WEEK
        self.MANUAL_REVIEW_THRESHOLD = settings.MANUAL_REVIEW_THRESHOLD

    def validate_action(self, action: Dict[str, Any], case: Dict[str, Any], customer: Dict[str, Any]) -> Dict[str, Any]:
        if case.get("status") == "RECOVERED":
            return {"result": "STOP_WORKFLOW", "reason": "Case already recovered"}
        if case.get("status") in ["STOPPED", "FAILED", "ESCALATED", "MANUAL_REVIEW"]:
            return {"result": "STOP_WORKFLOW", "reason": "Case already closed"}
        if customer.get("has_opted_out", False):
            return {"result": "STOP_WORKFLOW", "reason": "Customer opted out"}
        # Contact frequency + allowed hours gates
        if action.get("action_type") in ["SEND_NOTIFICATION", "UPDATE_PAYMENT_METHOD"]:
            if customer.get("contacts_last_7d", 0) >= self.MAX_CONTACTS_PER_WEEK:
                return {"result": "REJECTED", "reason": "Contact frequency limit reached"}
            from datetime import datetime
            hour = customer.get("current_hour", datetime.now().hour)
            if hour < 8 or hour > 20:
                return {"result": "REJECTED", "reason": "Outside allowed contact hours"}
        rc = case.get("current_retry_count", 0)
        mr = case.get("max_retries", self.MAX_RETRIES)
        if rc >= mr and action.get("action_type") in ["RETRY_PAYMENT", "DELAYED_RETRY"]:
            return {"result": "REJECTED", "reason": f"Max retries ({mr}) reached"}
        amt = case.get("amount_at_risk", 0)
        if amt > self.MANUAL_REVIEW_THRESHOLD and action.get("action_type") != "ESCALATE":
            return {"result": "REQUIRES_MANUAL_REVIEW", "reason": f"Amount ₹{amt:,.0f} exceeds threshold"}
        fr = case.get("root_cause", "")
        if fr in ["expired_card", "invalid_payment_method", "fraud_risk_block"] and action.get("action_type") in ["RETRY_PAYMENT", "DELAYED_RETRY"]:
            return {"result": "REJECTED", "reason": f"Permanent failure '{fr}'"}
        rec = case.get("recovered_amount", 0)
        at_risk = case.get("amount_at_risk", 0)
        if rec >= at_risk and at_risk > 0:
            return {"result": "STOP_WORKFLOW", "reason": "Full amount recovered"}
        return {"result": "APPROVED", "reason": "All policy checks passed"}
