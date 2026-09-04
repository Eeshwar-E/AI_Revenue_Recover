from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CaseBase(BaseModel):
    customer_id: int
    source_type: str
    amount_at_risk: float


class CaseResponse(BaseModel):
    id: int
    case_number: str
    customer_id: int
    customer_name: Optional[str] = None
    source_type: str
    amount_at_risk: float
    recovered_amount: float
    status: str
    risk_level: str
    risk_score: float
    root_cause: Optional[str] = None
    root_cause_detail: Optional[str] = None
    current_retry_count: int
    max_retries: int
    recommended_action: Optional[str] = None
    action_reasoning: Optional[str] = None
    confidence: float
    should_escalate: int
    stop_reason: Optional[str] = None
    last_action_at: Optional[datetime] = None
    next_action_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseDetail(CaseResponse):
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_segment: Optional[str] = None
    customer_lifetime_value: Optional[float] = None
    historical_success_rate: Optional[float] = None
    recent_success_rate: Optional[float] = None
    actions: List[dict] = []
    audit_events: List[dict] = []