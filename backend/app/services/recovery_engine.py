from sqlalchemy.orm import Session
from app.models.case import RevenueRiskCase
from app.models.recovery import RecoveryAction
from app.models.audit import AuditEvent
from app.integrations.mock_payment_provider import MockPaymentProvider
from app.integrations.mock_subscription_provider import MockSubscriptionProvider
from app.services.notification_service import NotificationService
from datetime import datetime
from typing import Dict, Any


class RecoveryEngine:
    def __init__(self, db: Session):
        self.db = db
        self.payment_provider = MockPaymentProvider()
        self.subscription_provider = MockSubscriptionProvider()
        self.notification_service = NotificationService(db)

    def execute_action(self, case: RevenueRiskCase, action_type: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        recovered = 0.0
        result = "PENDING"
        details = ""

        if action_type in ["RETRY_PAYMENT", "DELAYED_RETRY"]:
            pr = self.payment_provider.retry_payment(case.transaction_id or case.id)
            result = pr["status"]
            if result == "SUCCESS":
                recovered = case.amount_at_risk - case.recovered_amount
                details = f"Payment succeeded. Ref: {pr.get('gateway_reference', 'N/A')}"
            else:
                details = f"Failed. Reason: {pr.get('failure_reason', 'unknown')}"
        elif action_type == "UPDATE_PAYMENT_METHOD":
            result = "SUCCESS"
            details = "Payment method update request sent"
        elif action_type == "SEND_NOTIFICATION":
            result = "SENT"
            details = "Notification sent"
        elif action_type == "ESCALATE":
            result = "ESCALATED"
            details = "Case escalated to account manager"

        action_record = RecoveryAction(
            case_id=case.id, action_type=action_type, status=result,
            reason=strategy.get("description", ""),
            attempted_at=datetime.now(), result=details,
            recovered_amount=recovered, policy_result="APPROVED"
        )
        self.db.add(action_record)
        case.current_retry_count += 1
        case.last_action_at = datetime.now()

        if result == "SUCCESS" and recovered > 0:
            case.recovered_amount += recovered
            case.recovered_amount = min(case.recovered_amount, case.amount_at_risk)
            if case.recovered_amount >= case.amount_at_risk:
                case.status = "RECOVERED"
                case.stop_reason = "Revenue fully recovered"
            else:
                case.status = "RETRY_PENDING"
        elif result == "ESCALATED":
            case.status = "ESCALATED"
            case.should_escalate = 1
        elif case.current_retry_count >= case.max_retries:
            case.status = "STOPPED"
            case.stop_reason = f"Retries exhausted ({case.current_retry_count}/{case.max_retries})"
        else:
            case.status = "RETRY_PENDING"

        audit = AuditEvent(
            case_id=case.id, actor="AGENT",
            event_type="ACTION_EXECUTED",
            actual_action=action_type,
            action_result=result,
            recovery_amount=recovered,
            next_step=case.status,
            details=details,
            policy_result="APPROVED"
        )
        self.db.add(audit)
        self.db.commit()

        return {
            "action_type": action_type, "result": result,
            "recovered_amount": recovered,
            "details": details,
            "case_status": case.status,
            "total_recovered": case.recovered_amount,
            "retry_count": case.current_retry_count,
        }