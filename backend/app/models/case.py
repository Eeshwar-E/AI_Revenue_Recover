from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.models.base import Base, TimestampMixin


class RevenueRiskCase(Base, TimestampMixin):
    __tablename__ = "revenue_risk_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    source_type = Column(String, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    amount_at_risk = Column(Float, nullable=False)
    recovered_amount = Column(Float, default=0.0)
    status = Column(String, default="DETECTED")
    risk_level = Column(String, default="MEDIUM")
    risk_score = Column(Float, default=0.0)
    root_cause = Column(String, nullable=True)
    root_cause_detail = Column(String, nullable=True)
    current_retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    recommended_action = Column(String, nullable=True)
    action_reasoning = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    should_escalate = Column(Integer, default=0)
    stop_reason = Column(String, nullable=True)
    last_action_at = Column(DateTime, nullable=True)
    next_action_at = Column(DateTime, nullable=True)
    batch_id = Column(Integer, nullable=True)
    is_processed = Column(Integer, default=0)
