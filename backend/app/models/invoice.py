from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="PENDING")
    due_date = Column(DateTime, nullable=False)
    paid_amount = Column(Float, default=0.0)
    paid_date = Column(DateTime, nullable=True)
    days_overdue = Column(Integer, default=0)
    account_owner = Column(String, nullable=True)
    customer_segment = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
