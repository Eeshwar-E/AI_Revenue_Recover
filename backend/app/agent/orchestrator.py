from sqlalchemy.orm import Session
from app.models.case import RevenueRiskCase
from app.models.customer import Customer
from app.agent.state_machine import StateMachine, RecoveryState
from app.agent.decision_engine import DecisionEngine
from app.services.root_cause_engine import RootCauseEngine
from app.services.strategy_engine import StrategyEngine
from app.services.policy_engine import PolicyEngine
from app.services.recovery_engine import RecoveryEngine
from app.config import settings
from typing import Dict, Any, List
from datetime import datetime


class RecoveryOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.decision_engine = DecisionEngine(
            use_llm=settings.LLM_API_KEY is not None, api_key=settings.LLM_API_KEY)
        self.root_cause_engine = RootCauseEngine()
        self.strategy_engine = StrategyEngine()
        self.policy_engine = PolicyEngine()
        self.recovery_engine = RecoveryEngine(db)

    def run_case(self, case_id: int) -> Dict[str, Any]:
        case = self.db.query(RevenueRiskCase).filter(RevenueRiskCase.id == case_id).first()
        if not case:
            return {"error": f"Case {case_id} not found"}
        customer = self.db.query(Customer).filter(Customer.id == case.customer_id).first()
        if not customer:
            return {"error": f"Customer not found for case {case_id}"}

        steps: List[Dict[str, Any]] = []
        current_state = RecoveryState(case.status) if case.status in [s.value for s in RecoveryState] else RecoveryState.DETECTED

        # Step 1: Detect
        if current_state == RecoveryState.DETECTED:
            steps.append({"step": "DETECT", "message": f"Revenue risk detected: ₹{case.amount_at_risk:,.0f} for {customer.name}", "state": "DETECTED"})
            current_state = self.state_machine.transition(current_state, RecoveryState.DIAGNOSING)

        # Step 2: Diagnose
        if current_state == RecoveryState.DIAGNOSING:
            case_data = self._build_case_data(case, customer)
            decision = self.decision_engine.analyze_case(case_data)
            case.risk_score = decision["risk_score"]
            case.risk_level = decision["risk_level"]
            case.root_cause = decision["root_cause"]
            case.confidence = decision["confidence"]
            case.recommended_action = decision["recommended_action"]
            case.action_reasoning = decision["reasoning"]
            steps.append({"step": "DIAGNOSE", "message": f"Root cause: {decision['root_cause']}. Risk: {decision['risk_score']}/100. Confidence: {decision['confidence']*100:.0f}%", "state": "DIAGNOSING", "decision": decision})
            current_state = self.state_machine.transition(current_state, RecoveryState.STRATEGY_SELECTED)

        # Step 3: Strategy
        if current_state == RecoveryState.STRATEGY_SELECTED:
            case_data = self._build_case_data(case, customer)
            rc = self.root_cause_engine.analyze(case_data)
            strat = self.strategy_engine.select_strategy(rc, case_data)
            steps.append({"step": "STRATEGY_SELECTED", "message": f"Strategy: {strat['action_type']}. Expected recovery: ₹{strat['expected_recovery']:,.0f}", "state": "STRATEGY_SELECTED", "strategy": strat})
            current_state = self.state_machine.transition(current_state, RecoveryState.POLICY_CHECK)

        # Step 4: Policy Check
        if current_state == RecoveryState.POLICY_CHECK:
            case_dict = self._case_to_dict(case)
            cust_dict = {"has_opted_out": customer.has_opted_out}
            pol = self.policy_engine.validate_action({"action_type": case.recommended_action}, case_dict, cust_dict)
            steps.append({"step": "POLICY_CHECK", "message": f"Policy: {pol['result']}. {pol['reason']}", "state": "POLICY_CHECK", "policy_result": pol})
            if pol["result"] == "STOP_WORKFLOW":
                case.status = "STOPPED"
                case.stop_reason = pol["reason"]
                self.db.commit()
                return {"steps": steps, "final_status": "STOPPED", "recovered_amount": case.recovered_amount}
            if pol["result"] == "REQUIRES_MANUAL_REVIEW":
                case.status = "MANUAL_REVIEW"
                self.db.commit()
                return {"steps": steps, "final_status": "MANUAL_REVIEW", "recovered_amount": case.recovered_amount}
            if pol["result"] == "REJECTED":
                case.status = "STOPPED"
                case.stop_reason = pol["reason"]
                self.db.commit()
                return {"steps": steps, "final_status": "STOPPED", "recovered_amount": case.recovered_amount}
            current_state = self.state_machine.transition(current_state, RecoveryState.ACTION_PENDING)

        # Step 5: Execute
        if current_state == RecoveryState.ACTION_PENDING:
            strategy = {"description": case.action_reasoning}
            res = self.recovery_engine.execute_action(case, case.recommended_action, strategy)
            steps.append({"step": "EXECUTE", "message": f"Executed {case.recommended_action}. Result: {res['result']}. Recovered: ₹{res['recovered_amount']:,.0f}", "state": "ACTION_EXECUTED", "result": res})
            current_state = RecoveryState.ACTION_EXECUTED

        # Step 6: Verify
        if current_state == RecoveryState.ACTION_EXECUTED:
            if case.status == "RECOVERED":
                steps.append({"step": "VERIFY", "message": f"Payment verified. Total recovered: ₹{case.recovered_amount:,.0f}", "state": "VERIFYING"})
                current_state = RecoveryState.RECOVERED
            elif case.status == "ESCALATED":
                steps.append({"step": "ESCALATE", "message": "Case escalated. Human review required.", "state": "ESCALATED"})
            elif case.status == "STOPPED":
                steps.append({"step": "STOP", "message": f"Stopped: {case.stop_reason}", "state": "STOPPED"})
            else:
                steps.append({"step": "RETRY_PENDING", "message": f"Pending retry. Attempt {case.current_retry_count}/{case.max_retries}", "state": "RETRY_PENDING"})
            self.db.commit()
            return {"steps": steps, "final_status": case.status, "recovered_amount": case.recovered_amount, "case_id": case.id, "case_number": case.case_number}

        self.db.commit()
        return {"steps": steps, "final_status": case.status, "recovered_amount": case.recovered_amount, "case_id": case.id, "case_number": case.case_number}

    def _build_case_data(self, case: RevenueRiskCase, customer: Customer) -> Dict[str, Any]:
        return {
            "customer_id": customer.id, "customer_name": customer.name,
            "amount": case.amount_at_risk,
            "source_type": case.source_type,
            "failure_reason": case.root_cause or "unknown",
            "historical_success_rate": customer.historical_success_rate,
            "recent_success_rate": customer.recent_success_rate,
            "retry_count": case.current_retry_count,
        }

    def _case_to_dict(self, case: RevenueRiskCase) -> Dict[str, Any]:
        return {"status": case.status, "current_retry_count": case.current_retry_count, "max_retries": case.max_retries,
                "amount_at_risk": case.amount_at_risk, "recovered_amount": case.recovered_amount, "root_cause": case.root_cause}