from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin
from datetime import datetime


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    case_id = Column(Integer, ForeignKey("revenue_risk_cases.id"), nullable=True)
    batch_id = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    steps_executed = Column(Integer, default=0)
    decision = Column(String, nullable=True)
    actions = Column(String, nullable=True)
    result = Column(String, nullable=True)
    revenue_recovered = Column(Float, default=0.0)
    failure_reason = Column(String, nullable=True)
