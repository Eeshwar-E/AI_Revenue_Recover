from abc import ABC, abstractmethod
from typing import Dict, Any


class PaymentProvider(ABC):
    @abstractmethod
    def retry_payment(self, transaction_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_payment_status(self, transaction_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_payment(self, customer_id: int, amount: float, method: str) -> Dict[str, Any]:
        pass
