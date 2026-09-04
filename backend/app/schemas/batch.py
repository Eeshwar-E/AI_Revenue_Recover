from pydantic import BaseModel


class BatchResult(BaseModel):
    batch_id: int
    cases_processed: int
    total_at_risk: float
    recovered_amount: float
    recovered_this_batch: float
    recovery_rate: float
    successful_recoveries: int
    failed_cases: int
    escalated_cases: int
    stopped_cases: int
    actions_executed: int
    average_attempts: float
    duration_seconds: float