from typing import Dict, Any
from app.integrations.notification_provider import NotificationProvider


class MockNotificationProvider(NotificationProvider):
    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        return {"channel": "SMS", "status": "SENT", "recipient": phone, "message": message}

    def send_email(self, email: str, subject: str, body: str) -> Dict[str, Any]:
        return {"channel": "EMAIL", "status": "SENT", "recipient": email, "subject": subject}

    def send_in_app(self, customer_id: int, message: str) -> Dict[str, Any]:
        return {"channel": "IN_APP", "status": "SENT", "customer_id": customer_id, "message": message}
