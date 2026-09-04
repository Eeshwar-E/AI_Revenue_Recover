from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class AgentStep(BaseModel):
    step: str
    message: str
    state: Optional[str] = None
    decision: Optional[Dict[str, Any]] = None
    strategy: Optional[Dict[str, Any]] = None
    policy_result: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None


class AgentRunResult(BaseModel):
    steps: List[AgentStep]
    final_status: str
    recovered_amount: float
    case_id: Optional[int] = None
    case_number: Optional[str] = None
    error: Optional[str] = None


class AgentDecision(BaseModel):
    risk_score: float
    risk_level: str
    root_cause: str
    confidence: float
    recommended_action: str
    reasoning: str
    expected_recovery: float
    max_attempts: int
    should_escalate: bool
    stop_reason: Optional[str] = None