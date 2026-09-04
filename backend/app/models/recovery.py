from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.models.base import Base, TimestampMixin


class RecoveryAction(Base, TimestampMixin):
    __tablename__ = "recovery_actions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("revenue_risk_cases.id"), nullable=False)
    action_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    reason = Column(String, nullable=True)
    attempted_at = Column(DateTime, nullable=True)
    result = Column(String, nullable=True)
    recovered_amount = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    policy_result = Column(String, default="PENDING")
    metadata_json = Column(Text, nullable=True)
