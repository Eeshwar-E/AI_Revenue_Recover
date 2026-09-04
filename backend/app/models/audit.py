from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.models.base import Base, TimestampMixin


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("revenue_risk_cases.id"), nullable=True)
    batch_id = Column(Integer, nullable=True)
    actor = Column(String, default="AGENT")
    event_type = Column(String, nullable=False)
    risk_score = Column(Float, nullable=True)
    root_cause = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)
    policy_result = Column(String, nullable=True)
    actual_action = Column(String, nullable=True)
    action_result = Column(String, nullable=True)
    recovery_amount = Column(Float, default=0.0)
    next_step = Column(String, nullable=True)
    stop_reason = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=True)
