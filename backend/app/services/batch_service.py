from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.case import RevenueRiskCase
from app.services.risk_engine import RiskEngine
from app.services.root_cause_engine import RootCauseEngine
from app.services.strategy_engine import StrategyEngine
from app.services.policy_engine import PolicyEngine
from datetime import datetime


class BatchService:
    def __init__(self, db: Session):
        self.db = db
        self.risk_engine = RiskEngine(db)
        self.root_cause_engine = RootCauseEngine()
        self.strategy_engine = StrategyEngine()
        self.policy_engine = PolicyEngine()
        self.recovery_engine = None  # init per case

    def run_full_batch(self) -> Dict[str, Any]:
        start = datetime.now()
        cases = self.db.query(RevenueRiskCase).filter(
            RevenueRiskCase.status.notin_(["RECOVERED", "STOPPED", "FAILED"])
        ).all()
        total_at_risk = sum(c.amount_at_risk for c in cases)
        total_recovered_before = sum(c.recovered_amount for c in cases)
        counts = {"processed": 0, "successful": 0, "failed": 0, "escalated": 0, "stopped": 0, "actions": 0}
        for case in cases:
            result = self._process_single(case)
            counts["processed"] += 1
            if result["final_status"] == "RECOVERED":
                counts["successful"] += 1
            elif result["final_status"] == "ESCALATED":
                counts["escalated"] += 1
            elif result["final_status"] == "STOPPED":
                counts["stopped"] += 1
            elif result["final_status"] == "FAILED":
                counts["failed"] += 1
            counts["actions"] += result.get("actions_taken", 0)
        self.db.commit()
        total_after = sum(c.recovered_amount for c in cases)
        recovered = total_after - total_recovered_before
        duration = (datetime.now() - start).total_seconds()
        return {
            "batch_id": int(start.timestamp()),
            "cases_processed": counts["processed"],
            "total_at_risk": total_at_risk,
            "recovered_amount": total_after,
            "recovered_this_batch": recovered,
            "recovery_rate": round((total_after / max(total_at_risk, 1)) * 100, 1),
            "successful_recoveries": counts["successful"],
            "failed_cases": counts["failed"],
            "escalated_cases": counts["escalated"],
            "stopped_cases": counts["stopped"],
            "actions_executed": counts["actions"],
            "average_attempts": round(counts["actions"] / max(counts["processed"], 1), 1),
            "duration_seconds": round(duration, 2),
        }

    def _process_single(self, case: RevenueRiskCase) -> Dict[str, Any]:
        from app.models.customer import Customer
        customer = self.db.query(Customer).filter(Customer.id == case.customer_id).first()
        if not customer or case.status in ["RECOVERED", "STOPPED", "FAILED", "MANUAL_REVIEW"]:
            return {"final_status": case.status, "actions_taken": 0}
        cdata = {"source_type": case.source_type, "failure_reason": case.root_cause or "unknown",
                 "amount": case.amount_at_risk, "customer_name": customer.name,
                 "historical_success_rate": customer.historical_success_rate,
                 "recent_success_rate": customer.recent_success_rate, "retry_count": case.current_retry_count}
        rc = self.root_cause_engine.analyze(cdata)
        case.root_cause = rc["root_cause"]
        case.confidence = rc["confidence"]
        strat = self.strategy_engine.select_strategy(rc, cdata)
        case.recommended_action = strat["action_type"]
        case_dict = {"status": case.status, "current_retry_count": case.current_retry_count, "max_retries": case.max_retries,
                     "amount_at_risk": case.amount_at_risk, "recovered_amount": case.recovered_amount, "root_cause": case.root_cause}
        cust_dict = {"has_opted_out": customer.has_opted_out}
        pol = self.policy_engine.validate_action({"action_type": case.recommended_action}, case_dict, cust_dict)
        if pol["result"] == "STOP_WORKFLOW":
            case.status = "STOPPED"
            case.stop_reason = pol["reason"]
            return {"final_status": "STOPPED", "actions_taken": 0}
        if pol["result"] == "REQUIRES_MANUAL_REVIEW":
            case.status = "MANUAL_REVIEW"
            return {"final_status": "MANUAL_REVIEW", "actions_taken": 0}
        if pol["result"] == "REJECTED":
            if rc.get("retryable", True):
                case.status = "STOPPED"
                case.stop_reason = pol["reason"]
                return {"final_status": "STOPPED", "actions_taken": 0}
            else:
                case.status = "ESCALATED"
                case.should_escalate = 1
                return {"final_status": "ESCALATED", "actions_taken": 0}
        # Execute
        case.status = "ACTION_EXECUTED"
        res = self.recovery_engine.execute_action(case, case.recommended_action, strat) if self.recovery_engine else {"recovered_amount": 0, "result": "SUCCESS", "case_status": case.status}
        case.status = res["case_status"]
        actions_taken = 1
        return {"final_status": case.status, "actions_taken": actions_taken, "recovered": res.get("recovered_amount", 0)}