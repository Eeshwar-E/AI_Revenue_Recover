from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditEventResponse(BaseModel):
    id: int
    case_id: Optional[int] = None
    batch_id: Optional[int] = None
    actor: str
    event_type: str
    risk_score: Optional[float] = None
    root_cause: Optional[str] = None
    recommended_action: Optional[str] = None
    policy_result: Optional[str] = None
    actual_action: Optional[str] = None
    action_result: Optional[str] = None
    recovery_amount: float
    next_step: Optional[str] = None
    stop_reason: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True