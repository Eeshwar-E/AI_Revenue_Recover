from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.customer import Customer
from app.integrations.mock_notification_provider import MockNotificationProvider
from datetime import datetime, timedelta


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.provider = MockNotificationProvider()

    def send_payment_retry(self, customer: Customer, amount: float, case_number: str) -> Notification:
        msg = f"Your payment of ₹{amount:,.0f} could not be completed. Please retry. Ref: {case_number}"
        r = self.provider.send_sms(customer.phone, msg)
        n = Notification(customer_id=customer.id, channel="SMS", template="payment_retry", subject="Payment Retry Required", content=msg, status=r["status"])
        self.db.add(n)
        self.db.commit()
        return n

    def send_update_request(self, customer: Customer, case_number: str) -> Notification:
        msg = f"Please update your payment method. Ref: {case_number}"
        r = self.provider.send_email(customer.email, "Update Payment Method", msg)
        n = Notification(customer_id=customer.id, channel="EMAIL", template="payment_method_update", subject="Update Payment Method", content=msg, status=r["status"])
        self.db.add(n)
        self.db.commit()
        return n

    def can_contact(self, customer_id: int) -> bool:
        one_week_ago = datetime.now() - timedelta(days=7)
        count = self.db.query(Notification).filter(Notification.customer_id == customer_id, Notification.created_at >= one_week_ago).count()
        return count < 2
