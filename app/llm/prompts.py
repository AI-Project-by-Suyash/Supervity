import json
from typing import Dict, Any

SYSTEM_PROMPT = """You are an enterprise exception-resolution AI Employee.
Your job is to analyze transaction discrepancies based STRICTLY on the provided structured evidence.

CRITICAL RULES:
1. Use ONLY the supplied evidence fields.
2. NEVER invent transaction values, vendor history, or unstated business rules.
3. If evidence is missing or null, explicitly state that evidence is incomplete.
4. For suggestions, choose ONLY from the allowed actions:
   - REQUEST_VENDOR_CORRECTION
   - REQUEST_PAYMENT_REVIEW
   - REQUEST_QUANTITY_REVIEW
   - APPROVE_EXCEPTION
   - ESCALATE_TO_HUMAN
   - NO_ACTION
5. Return strictly valid JSON conforming to the requested schema.
"""

def build_explain_prompt(exception_data: Dict[str, Any], evidence_data: Dict[str, Any]) -> str:
    return f"""Analyze this transaction discrepancy and explain the root cause.

Exception Type: {exception_data.get('type')}
Severity: {exception_data.get('severity')}
Description: {exception_data.get('description')}
Expected: {exception_data.get('expected_value')}
Actual: {exception_data.get('actual_value')}
Difference: {exception_data.get('difference')}
Policy Threshold: {exception_data.get('threshold')}

Structured Evidence Records:
{json.dumps(evidence_data, indent=2)}

Output strictly valid JSON with this exact format:
{{
  "explanation": "concise 2-3 sentence root-cause explanation citing exact evidence values",
  "evidence_fields": ["list", "of", "exact", "field", "names", "cited"]
}}
"""

def build_suggest_prompt(exception_data: Dict[str, Any], evidence_data: Dict[str, Any]) -> str:
    return f"""Recommend a resolution for this transaction discrepancy.

Exception Type: {exception_data.get('type')}
Severity: {exception_data.get('severity')}
Description: {exception_data.get('description')}
Expected: {exception_data.get('expected_value')}
Actual: {exception_data.get('actual_value')}
Difference: {exception_data.get('difference')}

Structured Evidence Records:
{json.dumps(evidence_data, indent=2)}

Allowed Actions:
- REQUEST_VENDOR_CORRECTION (for invoice/PO price/tax discrepancy)
- REQUEST_PAYMENT_REVIEW (for overdue or terms mismatch)
- REQUEST_QUANTITY_REVIEW (for physical goods shipment shortfall/overdelivery)
- APPROVE_EXCEPTION (for acceptable minor variances within policy)
- ESCALATE_TO_HUMAN (for missing evidence, severe discrepancies, or ambiguous rules)
- NO_ACTION

Output strictly valid JSON with this exact format:
{{
  "suggested_action": "EXACT_ENUM_ACTION",
  "reason": "specific business reasoning based on evidence",
  "ai_score": 0.95,
  "evidence_fields": ["invoice.amount", "purchase_order.amount"]
}}
"""
