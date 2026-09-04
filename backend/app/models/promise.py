from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin


class PromiseToPay(Base, TimestampMixin):
    __tablename__ = "promise_to_pay"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("revenue_risk_cases.id"), nullable=True)
    promised_amount = Column(Float, nullable=False)
    promise_date = Column(DateTime, nullable=False)
    status = Column(String, default="PENDING")
    fulfilled_amount = Column(Float, default=0.0)
    fulfilled_at = Column(DateTime, nullable=True)
    reminder_count = Column(Integer, default=0)
    missed_count = Column(Integer, default=0)
    notes = Column(String, nullable=True)
