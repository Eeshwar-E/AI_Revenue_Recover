from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    failure_reason = Column(String, nullable=True)
    gateway_reference = Column(String, nullable=True)
