from typing import Dict, Any


class MockCRMProvider:
    def create_escalation(self, case_id: int, reason: str, priority: str) -> Dict[str, Any]:
        return {
            "escalation_id": f"ESC-{case_id}",
            "case_id": case_id,
            "reason": reason,
            "priority": priority,
            "status": "CREATED",
            "assigned_to": "Account Manager",
        }

    def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        return {"customer_id": customer_id, "interactions": [], "tickets": [], "notes": []}
