from sqlalchemy import Column, Integer, DateTime, func
from app.database import Base


class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
