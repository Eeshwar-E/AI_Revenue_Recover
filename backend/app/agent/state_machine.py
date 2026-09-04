from enum import Enum


class RecoveryState(str, Enum):
    DETECTED = "DETECTED"
    DIAGNOSING = "DIAGNOSING"
    STRATEGY_SELECTED = "STRATEGY_SELECTED"
    POLICY_CHECK = "POLICY_CHECK"
    ACTION_PENDING = "ACTION_PENDING"
    ACTION_EXECUTED = "ACTION_EXECUTED"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    RETRY_PENDING = "RETRY_PENDING"
    ESCALATED = "ESCALATED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


VALID_TRANSITIONS = {
    RecoveryState.DETECTED: [RecoveryState.DIAGNOSING, RecoveryState.STOPPED],
    RecoveryState.DIAGNOSING: [RecoveryState.STRATEGY_SELECTED, RecoveryState.STOPPED, RecoveryState.MANUAL_REVIEW],
    RecoveryState.STRATEGY_SELECTED: [RecoveryState.POLICY_CHECK, RecoveryState.STOPPED],
    RecoveryState.POLICY_CHECK: [RecoveryState.ACTION_PENDING, RecoveryState.STOPPED, RecoveryState.ESCALATED, RecoveryState.MANUAL_REVIEW],
    RecoveryState.ACTION_PENDING: [RecoveryState.ACTION_EXECUTED, RecoveryState.STOPPED],
    RecoveryState.ACTION_EXECUTED: [RecoveryState.VERIFYING, RecoveryState.RETRY_PENDING, RecoveryState.ESCALATED, RecoveryState.STOPPED, RecoveryState.RECOVERED],
    RecoveryState.VERIFYING: [RecoveryState.RECOVERED, RecoveryState.RETRY_PENDING, RecoveryState.FAILED],
    RecoveryState.RETRY_PENDING: [RecoveryState.ACTION_PENDING, RecoveryState.ESCALATED, RecoveryState.STOPPED],
    RecoveryState.RECOVERED: [],
    RecoveryState.ESCALATED: [],
    RecoveryState.STOPPED: [],
    RecoveryState.FAILED: [RecoveryState.RETRY_PENDING],
    RecoveryState.MANUAL_REVIEW: [],
}


class StateMachine:
    def __init__(self):
        self.transitions = VALID_TRANSITIONS

    def can_transition(self, from_state: RecoveryState, to_state: RecoveryState) -> bool:
        return to_state in self.transitions.get(from_state, [])

    def transition(self, current_state: RecoveryState, new_state: RecoveryState) -> RecoveryState:
        if not self.can_transition(current_state, new_state):
            raise ValueError(f"Invalid transition: {current_state} -> {new_state}")
        return new_state