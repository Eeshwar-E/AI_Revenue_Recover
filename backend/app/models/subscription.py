from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    plan_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="ACTIVE")
    payment_method = Column(String, nullable=False)
    mandate_id = Column(String, nullable=True)
    billing_cycle = Column(String, default="monthly")
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_date = Column(DateTime, nullable=True)
    failed_payment_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=True)
