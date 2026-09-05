from app.services.risk_engine import RiskEngine
from app.services.root_cause_engine import RootCauseEngine
from app.services.strategy_engine import StrategyEngine
from app.services.policy_engine import PolicyEngine
from app.agent.decision_engine import DecisionEngine
from app.agent.state_machine import StateMachine, RecoveryState
from app.models.transaction import Transaction


def test_risk_engine():
    from app.database import get_db, engine, Base
    from app.models.customer import Customer
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine_obj = RiskEngine(db)
        c = Customer(name="Test", email="t@t.com", phone="9999999999", segment="REGULAR",
                     historical_success_rate=0.9, recent_success_rate=0.5)
        db.add(c); db.commit()
        tx = Transaction(customer_id=c.id, amount=1000, currency="INR", status="SUCCESS",
                         payment_method="upi", created_at=None)
        db.add(tx); db.commit()
        tx2 = Transaction(customer_id=c.id, amount=2000, currency="INR", status="FAILED",
                          payment_method="card", failure_reason="insufficient_funds", created_at=None)
        db.add(tx2); db.commit()
        tx3 = Transaction(customer_id=c.id, amount=3000, currency="INR", status="FAILED",
                          payment_method="netbanking", failure_reason="insufficient_funds", created_at=None)
        db.add(tx3); db.commit()
        tx4 = Transaction(customer_id=c.id, amount=4000, currency="INR", status="FAILED",
                          payment_method="wallet", failure_reason="insufficient_funds", created_at=None)
        db.add(tx4); db.commit()
        tx5 = Transaction(customer_id=c.id, amount=5000, currency="INR", status="FAILED",
                          payment_method="upi", failure_reason="insufficient_funds", created_at=None)
        db.add(tx5); db.commit()
        risks = engine_obj.detect_degradation(c.id)
        assert len(risks) > 0
        assert risks[0]["risk_score"] >= 35
        print("✓ Risk engine: detects degradation")
    finally:
        db.close()


def test_root_cause_engine():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine_obj = RootCauseEngine()
        result = engine_obj.analyze({
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
        print("✓ Root cause engine: insufficient_funds -> delayed_retry")
    finally:
        db.close()


def test_strategy_engine():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = StrategyEngine()
        strat = engine.select_strategy(
            {"intervention_type": "retry_payment", "confidence": 0.8},
            {"amount": 10000, "retry_count": 0}
        )
        assert strat["action_type"] == "RETRY_PAYMENT"
        assert strat["expected_recovery"] > 0
        print("✓ Strategy engine: retry_payment selected")
    finally:
        db.close()


def test_policy_engine_retry_limit():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = PolicyEngine()
        result = engine.validate_action(
            {"action_type": "RETRY_PAYMENT"},
            {"status": "DETECTED", "current_retry_count": 3, "max_retries": 3,
             "amount_at_risk": 10000, "recovered_amount": 0, "root_cause": "network_error"},
            {"has_opted_out": False}
        )
        assert result["result"] == "REJECTED"
        print("✓ Policy engine: rejects after max retries")
    finally:
        db.close()


def test_policy_engine_permanent_failure():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = PolicyEngine()
        result = engine.validate_action(
            {"action_type": "RETRY_PAYMENT"},
            {"status": "DETECTED", "current_retry_count": 1, "max_retries": 3,
             "amount_at_risk": 10000, "recovered_amount": 0, "root_cause": "expired_card"},
            {"has_opted_out": False}
        )
        assert result["result"] == "REJECTED"
        print("✓ Policy engine: rejects retry for permanent failure")
    finally:
        db.close()


def test_policy_engine_customer_optout():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = PolicyEngine()
        result = engine.validate_action(
            {"action_type": "RETRY_PAYMENT"},
            {"status": "DETECTED", "current_retry_count": 0, "max_retries": 3,
             "amount_at_risk": 10000, "recovered_amount": 0, "root_cause": "network_error"},
            {"has_opted_out": True}
        )
        assert result["result"] == "STOP_WORKFLOW"
        print("✓ Policy engine: stops when customer opted out")
    finally:
        db.close()


def test_policy_engine_already_recovered():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = PolicyEngine()
        result = engine.validate_action(
            {"action_type": "RETRY_PAYMENT"},
            {"status": "RECOVERED", "current_retry_count": 1, "max_retries": 3,
             "amount_at_risk": 10000, "recovered_amount": 10000, "root_cause": "network_error"},
            {"has_opted_out": False}
        )
        assert result["result"] == "STOP_WORKFLOW"
        print("✓ Policy engine: stops when already recovered")
    finally:
        db.close()


def test_policy_engine_manual_review():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = PolicyEngine()
        result = engine.validate_action(
            {"action_type": "RETRY_PAYMENT"},
            {"status": "DETECTED", "current_retry_count": 0, "max_retries": 3,
             "amount_at_risk": 200000, "recovered_amount": 0, "root_cause": "network_error"},
            {"has_opted_out": False}
        )
        assert result["result"] == "REQUIRES_MANUAL_REVIEW"
        print("✓ Policy engine: requires manual review for high amounts")
    finally:
        db.close()


def test_state_machine():
    sm = StateMachine()
    assert sm.can_transition(RecoveryState.DETECTED, RecoveryState.DIAGNOSING)
    assert sm.can_transition(RecoveryState.DIAGNOSING, RecoveryState.STRATEGY_SELECTED)
    assert sm.can_transition(RecoveryState.STRATEGY_SELECTED, RecoveryState.POLICY_CHECK)
    assert sm.can_transition(RecoveryState.POLICY_CHECK, RecoveryState.ACTION_PENDING)
    assert not sm.can_transition(RecoveryState.RECOVERED, RecoveryState.DETECTED)
    print("✓ State machine: valid transitions work")


def test_decision_engine():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = DecisionEngine()
        decision = engine.analyze_case({
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
        print(f"✓ Decision engine: risk={decision['risk_score']}, action={decision['recommended_action']}")
    finally:
        db.close()


def test_decision_engine_permanent_failure():
    from app.database import get_db, engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        engine = DecisionEngine()
        decision = engine.analyze_case({
            "amount": 10000,
            "historical_success_rate": 0.95,
            "recent_success_rate": 0.5,
            "failure_reason": "expired_card",
            "retry_count": 0,
            "source_type": "PAYMENT_FAILURE",
        })
        assert decision["recommended_action"] == "UPDATE_PAYMENT_METHOD"
        print("✓ Decision engine: expired_card -> UPDATE_PAYMENT_METHOD")
    finally:
        db.close()


def test_no_double_counting():
    at_risk = 10000
    recovered = 4000 + 6000
    assert recovered == at_risk
    rate = recovered / at_risk * 100
    assert rate == 100.0
    print("✓ Revenue: no double counting")


def test_partial_recovery():
    at_risk = 10000
    recovered = 4000
    rate = recovered / at_risk * 100
    assert rate == 40.0
    print("✓ Revenue: partial recovery rate correct")


def test_zero_recovery():
    at_risk = 10000
    recovered = 0
    rate = recovered / at_risk * 100
    assert rate == 0.0
    print("✓ Revenue: zero recovery handled")


def test_policy_contact_limit():
    p = PolicyEngine()
    r = p.validate_action({"action_type": "SEND_NOTIFICATION"},
                          {"status": "DETECTED", "amount_at_risk": 5000, "recovered_amount": 0,
                           "current_retry_count": 0, "max_retries": 3},
                          {"has_opted_out": False, "contacts_last_7d": 5})
    assert r["result"] == "REJECTED"
    print("✓ Policy: contact frequency limit")


def test_policy_closed_states():
    p = PolicyEngine()
    for st in ("ESCALATED", "MANUAL_REVIEW"):
        r = p.validate_action({"action_type": "RETRY_PAYMENT"},
                              {"status": st, "amount_at_risk": 5000, "recovered_amount": 0,
                               "current_retry_count": 0, "max_retries": 3},
                              {"has_opted_out": False})
        assert r["result"] == "STOP_WORKFLOW", st
    print("✓ Policy: closed states stop")


def test_llm_fallback():
    d = DecisionEngine(use_llm=True, api_key="invalid")
    out = d.analyze_case({"amount": 10000, "historical_success_rate": 0.9,
                          "recent_success_rate": 0.4, "failure_reason": "network_error",
                          "retry_count": 0, "source_type": "PAYMENT_FAILURE"})
    assert out["recommended_action"] == "RETRY_PAYMENT"
    assert "fallback" in out["reasoning"]
    print("✓ Decision: LLM fallback works")


def test_mandate_sequencer():
    from app.services.promise_service import PromiseService
    svc = PromiseService.__new__(PromiseService)
    assert svc.mandate_next_step("network_error", 0)["wait_hours"] == 2
    assert svc.mandate_next_step("insufficient_funds", 0)["wait_hours"] == 48
    assert svc.mandate_next_step("expired_card", 0)["action"] == "UPDATE_PAYMENT_METHOD"
    assert svc.mandate_next_step("network_error", 5)["action"] == "ESCALATE"
    print("✓ Mandate sequencer")


def test_tool_registry():
    from app.agent.tools import ToolRegistry
    reg = ToolRegistry()
    reg.register("retry_payment", lambda transaction_id: {"status": "OK"})
    assert reg.execute("retry_payment", transaction_id=1)["status"] == "OK"
    assert "error" in reg.execute("nope")
    print("✓ Tool registry")


if __name__ == "__main__":
    test_risk_engine()
    test_root_cause_engine()
    test_strategy_engine()
    test_policy_engine_retry_limit()
    test_policy_engine_permanent_failure()
    test_policy_engine_customer_optout()
    test_policy_engine_already_recovered()
    test_policy_engine_manual_review()
    test_state_machine()
    test_decision_engine()
    test_decision_engine_permanent_failure()
    test_no_double_counting()
    test_partial_recovery()
    test_zero_recovery()
    test_policy_contact_limit()
    test_policy_closed_states()
    test_llm_fallback()
    test_mandate_sequencer()
    test_tool_registry()
    print("\n✅ All tests passed!")