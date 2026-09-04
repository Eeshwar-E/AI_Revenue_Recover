from typing import Dict, Any


class SubscriptionProvider:
    def retry_subscription_payment(self, subscription_id: int) -> Dict[str, Any]:
        raise NotImplementedError

    def update_payment_method(self, subscription_id: int, new_method: str) -> Dict[str, Any]:
        raise NotImplementedError


class MockSubscriptionProvider(SubscriptionProvider):
    _outcomes = {}

    def retry_subscription_payment(self, subscription_id: int) -> Dict[str, Any]:
        import random
        if subscription_id not in self._outcomes:
            self._outcomes[subscription_id] = random.random() < 0.55
        success = self._outcomes[subscription_id]
        return {
            "subscription_id": subscription_id,
            "status": "SUCCESS" if success else "FAILED",
            "failure_reason": None if success else random.choice(["insufficient_funds", "expired_card", "mandate_failure"]),
        }

    def update_payment_method(self, subscription_id: int, new_method: str) -> Dict[str, Any]:
        return {"subscription_id": subscription_id, "status": "UPDATED", "new_method": new_method}
