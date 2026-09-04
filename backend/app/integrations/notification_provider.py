from abc import ABC, abstractmethod
from typing import Dict, Any


class NotificationProvider(ABC):
    @abstractmethod
    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def send_email(self, email: str, subject: str, body: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def send_in_app(self, customer_id: int, message: str) -> Dict[str, Any]:
        pass
