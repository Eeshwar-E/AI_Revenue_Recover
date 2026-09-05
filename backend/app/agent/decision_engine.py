from typing import Dict, Any


class DecisionEngine:
    def __init__(self, use_llm: bool = False, api_key: str = None):
        self.use_llm = use_llm and api_key is not None
        self.api_key = api_key

    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_llm:
            try:
                return self._llm_analyze(case_data)
            except Exception:
                pass
        return self._deterministic_analyze(case_data)

    def _deterministic_analyze(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        amount = case_data.get("amount", 0)
        hist = case_data.get("historical_success_rate", 0.9)
        recent = case_data.get("recent_success_rate", 0.5)
        failure = case_data.get("failure_reason", "unknown")
        retry_count = case_data.get("retry_count", 0)
        days = case_data.get("days_overdue", 0)
        source_type = case_data.get("source_type", "PAYMENT_FAILURE")

        risk_score = 50
        if recent < 0.5:
            risk_score += 20
        elif recent < 0.7:
            risk_score += 10
        if hist > 0.85 and recent < 0.7:
            risk_score += 15
        if retry_count > 0:
            risk_score += retry_count * 5
        if days > 30:
            risk_score += 15
        elif days > 14:
            risk_score += 10
        elif days > 7:
            risk_score += 5
        risk_score = min(max(risk_score, 0), 100)

        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        permanent_failures = ["expired_card", "invalid_payment_method", "fraud_risk_block"]
        is_permanent = failure in permanent_failures
        if is_permanent:
            if source_type in ["PAYMENT_FAILURE", "SUBSCRIPTION"]:
                action = "UPDATE_PAYMENT_METHOD"
                reasoning = f"Permanent failure '{failure}'. Customer must update payment method."
            else:
                action = "ESCALATE"
                reasoning = f"Permanent issue detected: '{failure}'. Requires human intervention."
        elif retry_count >= 3:
            action = "ESCALATE"
            reasoning = f"Maximum retries ({retry_count}) exhausted. Escalating to human."
        elif source_type == "RECEIVABLE":
            if days > 30:
                action = "ESCALATE"
                reasoning = f"Invoice overdue {days} days. Escalating."
            elif days > 14:
                action = "SEND_NOTIFICATION"
                reasoning = f"Invoice overdue {days} days. Personalized follow-up."
            else:
                action = "SEND_NOTIFICATION"
                reasoning = f"Recent overdue {days} days. Automated reminder."
        elif source_type == "CHECKOUT":
            action = "SEND_NOTIFICATION"
            reasoning = "Checkout abandoned. Sending recovery reminder."
        elif source_type == "MANDATE":
            action = "RETRY_PAYMENT"
            reasoning = "Mandate failure. Retry payment."
        else:
            if hist > 0.85:
                action = "RETRY_PAYMENT"
                reasoning = f"High success rate ({hist*100:.0f}%). Retry likely to succeed."
            elif hist > 0.7:
                action = "DELAYED_RETRY"
                reasoning = f"Moderate success rate ({hist*100:.0f}%). Delayed retry recommended."
            else:
                action = "ESCALATE"
                reasoning = f"Low success rate ({hist*100:.0f}%). Escalating."

        base_rate = 0.55 if not is_permanent else 0.0
        if action == "ESCALATE":
            base_rate = 0.65
        expected_recovery = amount * base_rate * (0.85 ** retry_count)
        max_attempts = 3 if not is_permanent else 1
        should_escalate = action == "ESCALATE" or risk_level == "CRITICAL"
        confidence = min(max(0.7 + (0.15 if hist > 0.85 and not is_permanent else 0) - (retry_count * 0.1), 0.3), 0.95)
        stop_reason = None
        if is_permanent:
            stop_reason = f"Permanent failure: {failure}"
        elif retry_count >= max_attempts:
            stop_reason = f"Maximum attempts ({max_attempts}) reached"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "root_cause": failure,
            "confidence": round(confidence, 2),
            "recommended_action": action,
            "reasoning": reasoning,
            "expected_recovery": round(expected_recovery, 2),
            "max_attempts": max_attempts,
            "should_escalate": should_escalate,
            "stop_reason": stop_reason,
            "is_permanent_failure": is_permanent,
        }

    def _llm_analyze(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """LLM provider interface with structured-JSON retry + deterministic fallback (§5)."""
        import json
        last_err = None
        for _ in range(2):
            try:
                payload = self._call_llm(case_data)
                decision = json.loads(payload) if isinstance(payload, str) else dict(payload)
                # Validate required shape
                for k in ("risk_score", "risk_level", "root_cause", "recommended_action"):
                    if k not in decision:
                        raise ValueError(f"LLM response missing key: {k}")
                decision.setdefault("confidence", 0.6)
                decision.setdefault("reasoning", "LLM recommendation (validated)")
                decision.setdefault("expected_recovery", 0)
                decision.setdefault("max_attempts", 3)
                decision.setdefault("should_escalate", False)
                decision.setdefault("stop_reason", None)
                return decision
            except Exception as e:
                last_err = e
        # Fallback to deterministic rules
        d = self._deterministic_analyze(case_data)
        d["reasoning"] = f"{d['reasoning']} (deterministic fallback; LLM unavailable: {last_err})"
        return d

    def _call_llm(self, case_data: Dict[str, Any]) -> str:
        """Replaceable provider: uses httpx against OpenAI-compatible chat endpoint if configured."""
        import os
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY not configured")
        import httpx
        base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        prompt = ("Return ONLY JSON with keys risk_score(0-100), risk_level(LOW|MEDIUM|HIGH|CRITICAL), "
                  f"root_cause, confidence(0-1), recommended_action, reasoning, expected_recovery, max_attempts, should_escalate, stop_reason. Case: {case_data}")
        r = httpx.post(f"{base}/chat/completions",
                       headers={"Authorization": f"Bearer {self.api_key}"},
                       json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0},
                       timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]