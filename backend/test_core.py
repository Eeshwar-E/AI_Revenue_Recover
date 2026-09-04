import sys
sys.path.insert(0, r'C:\Sheesh\Projects\Razorpay_Buildathon\backend')

# Test root cause engine
from app.services.root_cause_engine import RootCauseEngine
engine = RootCauseEngine()
result = engine.analyze({
    "source_type": "PAYMENT_FAILURE",
    "failure_reason": "insufficient_funds",
    "amount": 10000,
    "historical_success_rate": 0.95,
    "recent_success_rate": 0.5,
    "retry_count": 0,
    "customer_name": "Test"
})
assert result["root_cause"] == "insufficient_funds"
assert result["intervention_type"] == "delayed_retry"
assert result["retryable"] == True
assert result["is_permanent"] == False
print("PASS: Root cause engine insufficient_funds")

# Test decision engine
from app.agent.decision_engine import DecisionEngine
dec_engine = DecisionEngine()
decision = dec_engine.analyze_case({
    "amount": 10000,
    "historical_success_rate": 0.95,
    "recent_success_rate": 0.5,
    "failure_reason": "insufficient_funds",
    "retry_count": 0,
    "source_type": "PAYMENT_FAILURE",
})
assert 0 <= decision["risk_score"] <= 100
assert decision["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
assert decision["recommended_action"] in ["RETRY_PAYMENT", "DELAYED_RETRY", "UPDATE_PAYMENT_METHOD", "SEND_NOTIFICATION", "ESCALATE"]
print("PASS: Decision engine risk=%d action=%s" % (decision["risk_score"], decision["recommended_action"]))

# Test policy engine
from app.services.policy_engine import PolicyEngine
pol_engine = PolicyEngine()
result = pol_engine.validate_action(
    {"action_type": "RETRY_PAYMENT"},
    {"status": "DETECTED", "current_retry_count": 0, "max_retries": 3,
     "amount_at_risk": 10000, "recovered_amount": 0, "root_cause": "network_error"},
    {"has_opted_out": False}
)
assert result["result"] == "APPROVED"
print("PASS: Policy engine approve")

# Test state machine
from app.agent.state_machine import StateMachine, RecoveryState
sm = StateMachine()
assert sm.can_transition(RecoveryState.DETECTED, RecoveryState.DIAGNOSING)
assert sm.can_transition(RecoveryState.DIAGNOSING, RecoveryState.STRATEGY_SELECTED)
assert not sm.can_transition(RecoveryState.RECOVERED, RecoveryState.DETECTED)
print("PASS: State machine transitions")

print("\nAll core tests passed!")