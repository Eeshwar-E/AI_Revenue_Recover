from typing import Dict, Any


class RootCauseEngine:
    TAXONOMY = {
        "PAYMENT_FAILURE": {
            "insufficient_funds": {"intervention": "delayed_retry", "retryable": True, "permanent": False},
            "bank_decline": {"intervention": "retry_payment", "retryable": True, "permanent": False},
            "expired_card": {"intervention": "payment_method_update", "retryable": False, "permanent": True},
            "invalid_payment_method": {"intervention": "payment_method_update", "retryable": False, "permanent": True},
            "network_error": {"intervention": "retry_payment", "retryable": True, "permanent": False},
            "authentication_failure": {"intervention": "retry_payment", "retryable": True, "permanent": False},
            "fraud_risk_block": {"intervention": "escalate", "retryable": False, "permanent": True},
            "unknown": {"intervention": "retry_payment", "retryable": True, "permanent": False},
        },
        "SUBSCRIPTION": {
            "expired_payment_method": {"intervention": "payment_method_update", "retryable": False, "permanent": True},
            "mandate_failure": {"intervention": "mandate_retry", "retryable": True, "permanent": False},
            "insufficient_funds": {"intervention": "delayed_retry", "retryable": True, "permanent": False},
            "recurring_payment_decline": {"intervention": "retry_payment", "retryable": True, "permanent": False},
        },
        "CHECKOUT": {
            "user_abandoned": {"intervention": "send_reminder", "retryable": True, "permanent": False},
            "payment_method_failure": {"intervention": "alternative_payment_method", "retryable": True, "permanent": False},
            "technical_error": {"intervention": "retry_payment", "retryable": True, "permanent": False},
            "timeout": {"intervention": "send_reminder", "retryable": True, "permanent": False},
            "unknown": {"intervention": "send_reminder", "retryable": True, "permanent": False},
        },
        "RECEIVABLE": {
            "invoice_overdue": {"intervention": "automated_reminder", "retryable": True, "permanent": False},
            "missed_promise": {"intervention": "escalate", "retryable": True, "permanent": False},
            "customer_delay": {"intervention": "personalized_followup", "retryable": True, "permanent": False},
            "dispute": {"intervention": "escalate", "retryable": False, "permanent": False},
            "account_issue": {"intervention": "escalate", "retryable": False, "permanent": False},
        },
        "MANDATE": {
            "mandate_failure": {"intervention": "mandate_retry", "retryable": True, "permanent": False},
            "insufficient_funds": {"intervention": "delayed_retry", "retryable": True, "permanent": False},
            "network_error": {"intervention": "retry_payment", "retryable": True, "permanent": False},
        },
    }

    def analyze(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        source_type = case_data.get("source_type", "PAYMENT_FAILURE")
        failure_reason = case_data.get("failure_reason", "unknown")
        taxonomy = self.TAXONOMY.get(source_type, self.TAXONOMY["PAYMENT_FAILURE"])
        cause = taxonomy.get(failure_reason, {"intervention": "retry_payment", "retryable": True, "permanent": False})
        confidence = self._calc_confidence(case_data, cause)
        return {
            "root_cause": failure_reason,
            "root_cause_category": source_type,
            "intervention_type": cause["intervention"],
            "retryable": cause["retryable"],
            "is_permanent": cause["permanent"],
            "confidence": confidence,
            "reasoning": self._reasoning(case_data, failure_reason, cause),
        }

    def _calc_confidence(self, case_data: Dict, cause: Dict) -> float:
        base = 0.7
        hr = case_data.get("historical_success_rate", 0.9)
        if hr > 0.85 and not cause["permanent"]:
            base += 0.1
        rc = case_data.get("retry_count", 0)
        if rc > 0:
            base -= rc * 0.1
        return min(max(round(base, 2), 0.1), 0.99)

    def _reasoning(self, case_data: Dict, fr: str, cause: Dict) -> str:
        name = case_data.get("customer_name", "Customer")
        amt = case_data.get("amount", 0)
        hr = case_data.get("historical_success_rate", 0.9)
        rr = case_data.get("recent_success_rate", 0.5)
        sigs = []
        if hr > 0.85:
            sigs.append(f"Historical success rate {hr*100:.0f}%")
        if rr < 0.7:
            sigs.append(f"Recent rate dropped to {rr*100:.0f}%")
        if fr in ["network_error", "insufficient_funds", "bank_decline"]:
            sigs.append(f"'{fr}' is typically temporary")
        if fr in ["expired_card", "invalid_payment_method"]:
            sigs.append(f"'{fr}' requires payment method update")
        sig_str = "; ".join(sigs) if sigs else f"Failure: {fr}"
        return f"Analysis for {name} (₹{amt:,.0f}): {sig_str}. Intervention: {cause['intervention']}."
