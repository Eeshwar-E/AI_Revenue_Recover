import random
from typing import Dict, Any
from app.integrations.payment_provider import PaymentProvider


class MockPaymentProvider(PaymentProvider):
    _outcomes: Dict[int, bool] = {}

    def retry_payment(self, transaction_id: int) -> Dict[str, Any]:
        if transaction_id not in self._outcomes:
            self._outcomes[transaction_id] = random.random() < 0.60
        success = self._outcomes[transaction_id]
        reasons = ["insufficient_funds", "bank_decline", "network_error", "expired_card"]
        return {
            "transaction_id": transaction_id,
            "status": "SUCCESS" if success else "FAILED",
            "amount": 0,
            "gateway_reference": f"MOCK-GW-{transaction_id}-{random.randint(1000, 9999)}",
            "failure_reason": None if success else random.choice(reasons),
        }

    def get_payment_status(self, transaction_id: int) -> Dict[str, Any]:
        return {
            "transaction_id": transaction_id,
            "status": "SUCCESS" if self._outcomes.get(transaction_id, False) else "FAILED",
        }

    def create_payment(self, customer_id: int, amount: float, method: str) -> Dict[str, Any]:
        tx_id = random.randint(10000, 99999)
        success = random.random() < 0.65
        self._outcomes[tx_id] = success
        return {
            "transaction_id": tx_id,
            "status": "SUCCESS" if success else "FAILED",
            "amount": amount,
            "payment_method": method,
            "gateway_reference": f"MOCK-GW-{tx_id}-{random.randint(1000, 9999)}",
            "failure_reason": None if success else "payment_declined",
        }
