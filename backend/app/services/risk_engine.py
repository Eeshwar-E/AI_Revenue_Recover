from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.customer import Customer
from app.models.transaction import Transaction
from typing import Dict, Any, List
from datetime import datetime


class RiskEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_risk_score(self, customer: Customer, transactions: List[Transaction]) -> Dict[str, Any]:
        if not transactions:
            return {"risk_score": 50, "risk_level": "MEDIUM"}
        recent = transactions[:20]
        failures = [t for t in recent if t.status == "FAILED"]
        failure_rate = len(failures) / max(len(recent), 1)
        score = failure_rate * 60 + (1 - customer.historical_success_rate) * 20
        score = min(max(score, 0), 100)
        if score >= 80:
            level = "CRITICAL"
        elif score >= 60:
            level = "HIGH"
        elif score >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"
        return {"risk_score": round(score, 1), "risk_level": level}

    def detect_degradation(self, customer_id: int) -> List[Dict[str, Any]]:
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return []
        transactions = self.db.query(Transaction).filter(
            Transaction.customer_id == customer_id
        ).order_by(Transaction.id.desc()).all()
        if len(transactions) < 5:
            return []
        risk = self.calculate_risk_score(customer, transactions)
        if risk["risk_score"] >= 35:
            return [{
                "customer_id": customer_id,
                "customer_name": customer.name,
                "risk_score": risk["risk_score"],
                "risk_level": risk["risk_level"],
                "recent_failures": len([t for t in transactions[:10] if t.status == "FAILED"]),
                "total_recent": min(len(transactions), 10),
            }]
        return []

    def scan_all_customers(self) -> List[Dict[str, Any]]:
        customers = self.db.query(Customer).filter(Customer.is_active == 1).all()
        risks = []
        for c in customers:
            risks.extend(self.detect_degradation(c.id))
        return risks
