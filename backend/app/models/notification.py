from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.models.base import Base, TimestampMixin


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("revenue_risk_cases.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    channel = Column(String, nullable=False)
    template = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    status = Column(String, default="SENT")
    sent_at = Column(DateTime, nullable=True)
