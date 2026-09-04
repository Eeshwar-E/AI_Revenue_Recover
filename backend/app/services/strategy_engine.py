from typing import Dict, Any


class StrategyEngine:
    STRATEGIES = {
        "retry_payment": {"action_type": "RETRY_PAYMENT", "max_attempts": 3, "cooldown_hours": 2, "expected_recovery_rate": 0.55, "description": "Retry the failed payment"},
        "delayed_retry": {"action_type": "DELAYED_RETRY", "max_attempts": 3, "cooldown_hours": 24, "expected_recovery_rate": 0.45, "description": "Retry after a delay"},
        "payment_method_update": {"action_type": "UPDATE_PAYMENT_METHOD", "max_attempts": 2, "cooldown_hours": 48, "expected_recovery_rate": 0.70, "description": "Request payment method update"},
        "mandate_retry": {"action_type": "RETRY_PAYMENT", "max_attempts": 3, "cooldown_hours": 12, "expected_recovery_rate": 0.50, "description": "Retry mandate payment"},
        "send_reminder": {"action_type": "SEND_NOTIFICATION", "max_attempts": 2, "cooldown_hours": 24, "expected_recovery_rate": 0.35, "description": "Send payment reminder"},
        "automated_reminder": {"action_type": "SEND_NOTIFICATION", "max_attempts": 3, "cooldown_hours": 48, "expected_recovery_rate": 0.40, "description": "Automated overdue reminder"},
        "personalized_followup": {"action_type": "SEND_NOTIFICATION", "max_attempts": 2, "cooldown_hours": 72, "expected_recovery_rate": 0.50, "description": "Personalized follow-up"},
        "alternative_payment_method": {"action_type": "UPDATE_PAYMENT_METHOD", "max_attempts": 1, "cooldown_hours": 24, "expected_recovery_rate": 0.60, "description": "Suggest alternative method"},
        "escalate": {"action_type": "ESCALATE", "max_attempts": 1, "cooldown_hours": 0, "expected_recovery_rate": 0.65, "description": "Escalate to human"},
    }

    def select_strategy(self, root_cause: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]:
        intervention = root_cause.get("intervention_type", "retry_payment")
        s = self.STRATEGIES.get(intervention, self.STRATEGIES["retry_payment"]).copy()
        amount = case_data.get("amount", 0)
        retry_count = case_data.get("retry_count", 0)
        confidence = root_cause.get("confidence", 0.7)
        if amount > 100000 and intervention in ["retry_payment", "delayed_retry"]:
            s["expected_recovery_rate"] *= 0.9
        s["expected_recovery_rate"] *= (0.85 ** retry_count)
        expected_recovery = amount * s["expected_recovery_rate"]
        return {
            "strategy_name": intervention,
            "action_type": s["action_type"],
            "max_attempts": s["max_attempts"],
            "cooldown_hours": s["cooldown_hours"],
            "expected_recovery_rate": round(s["expected_recovery_rate"], 2),
            "expected_recovery": round(expected_recovery, 2),
            "description": s["description"],
            "confidence": confidence,
            "reasoning": f"Selected {intervention}. Expected recovery: ₹{expected_recovery:,.0f} ({s['expected_recovery_rate']*100:.0f}% of ₹{amount:,.0f}).",
        }
