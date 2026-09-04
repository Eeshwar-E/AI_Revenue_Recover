from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    segment = Column(String, default="REGULAR")
    lifetime_value = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    historical_success_rate = Column(Float, default=0.95)
    recent_success_rate = Column(Float, default=0.95)
    is_active = Column(Integer, default=1)
    has_opted_out = Column(Integer, default=0)
