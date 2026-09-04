from typing import Dict, Any, Callable


TOOLS = {
    "get_payment_history": {"name": "get_payment_history", "description": "Get customer payment history", "parameters": {"customer_id": "integer"}},
    "get_customer_profile": {"name": "get_customer_profile", "description": "Get customer profile", "parameters": {"customer_id": "integer"}},
    "get_invoice": {"name": "get_invoice", "description": "Get invoice details", "parameters": {"invoice_id": "integer"}},
    "get_subscription": {"name": "get_subscription", "description": "Get subscription details", "parameters": {"subscription_id": "integer"}},
    "get_payment_status": {"name": "get_payment_status", "description": "Check payment status", "parameters": {"transaction_id": "integer"}},
    "retry_payment": {"name": "retry_payment", "description": "Retry failed payment", "parameters": {"transaction_id": "integer"}},
    "send_notification": {"name": "send_notification", "description": "Send notification to customer", "parameters": {"customer_id": "integer", "channel": "string", "message": "string"}},
    "create_escalation": {"name": "create_escalation", "description": "Create escalation for case", "parameters": {"case_id": "integer", "reason": "string", "priority": "string"}},
    "create_promise_to_pay": {"name": "create_promise_to_pay", "description": "Create promise to pay record", "parameters": {"invoice_id": "integer", "amount": "float", "date": "string"}},
    "check_policy": {"name": "check_policy", "description": "Validate action against policy", "parameters": {"action_type": "string", "case_id": "integer"}},
}


class ToolRegistry:
    def __init__(self):
        self._impl: Dict[str, Callable] = {}

    def register(self, name: str, impl: Callable):
        self._impl[name] = impl

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        if name in self._impl:
            return self._impl[name](**kwargs)
        return {"error": f"Unknown tool: {name}"}

    def list_tools(self) -> list:
        return [{"name": t["name"], "description": t["description"], "parameters": t["parameters"]} for t in TOOLS.values()]