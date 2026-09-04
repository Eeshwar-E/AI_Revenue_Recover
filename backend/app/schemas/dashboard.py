from pydantic import BaseModel
from typing import List, Optional


class DashboardSummary(BaseModel):
    total_revenue_at_risk: float
    total_revenue_recovered: float
    active_revenue_at_risk: float
    recovery_rate: float
    total_cases: int
    active_cases: int
    recovered_cases: int
    escalated_cases: int
    failed_cases: int


class RecoveryByType(BaseModel):
    type: str
    recovered: float
    at_risk: float
    count: int


class RecoveryByAction(BaseModel):
    action_type: str
    recovered: float
    count: int


class RiskDistribution(BaseModel):
    risk_level: str
    count: int
    amount: float


class FunnelStage(BaseModel):
    stage: str
    count: int


class FailureReason(BaseModel):
    reason: str
    count: int