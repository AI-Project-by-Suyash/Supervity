from typing import Dict, Any, Tuple
from app.models.exception import ExceptionType

class ConfidenceEngine:
    """
    Calculates composite resolution confidence and evaluates deterministic safety gates.
    Formula:
      confidence = 0.30 * evidence_score + 0.30 * rule_certainty + 0.20 * classification_score + 0.20 * ai_score
    """
    def evaluate_safety_gates(self, exception_type: str, evidence_data: Dict[str, Any]) -> Tuple[bool, str]:
        # Gate 1: Check evidence completeness
        completeness = evidence_data.get('completeness_score', 1.0)
        if completeness < 0.70:
            return False, "Evidence completeness below safety threshold (<70%)."

        # Gate 2: Check for null mandatory fields
        fields = evidence_data.get('fields', [])
        for f in fields:
            if f.get('value') is None:
                return False, f"Mandatory evidence field '{f.get('name')}' is null/missing."

        # Gate 3: Auto-resolvable exception types check
        auto_resolvable_types = {
            ExceptionType.AMOUNT_MISMATCH.value,
            ExceptionType.QUANTITY_MISMATCH.value,
            ExceptionType.PAYMENT_OVERDUE.value
        }
        if exception_type not in auto_resolvable_types:
            return False, f"Exception type '{exception_type}' is not auto-resolvable."

        return True, "All safety gates passed."

    def calculate_confidence(
        self,
        exception_type: str,
        evidence_data: Dict[str, Any],
        ai_score: float = 0.90
    ) -> Dict[str, Any]:
        evidence_score = float(evidence_data.get('completeness_score', 1.0))
        
        # Rule certainty based on type definition clarity
        if evidence_score >= 0.95:
            rule_certainty = 0.95
        elif evidence_score >= 0.80:
            rule_certainty = 0.85
        else:
            rule_certainty = 0.70

        classification_score = 1.0 if exception_type in [e.value for e in ExceptionType] else 0.50
        bounded_ai_score = max(0.0, min(1.0, float(ai_score)))

        composite = (
            (0.30 * evidence_score) +
            (0.30 * rule_certainty) +
            (0.20 * classification_score) +
            (0.20 * bounded_ai_score)
        )
        composite = round(min(1.0, max(0.0, composite)), 4)

        safety_passed, gate_reason = self.evaluate_safety_gates(exception_type, evidence_data)

        # Policy decision mapping
        if composite >= 0.90 and safety_passed:
            decision = "AUTO_RESOLVE"
        elif composite >= 0.70:
            decision = "HUMAN_REVIEW"
        else:
            decision = "ESCALATE"

        return {
            "confidence": composite,
            "safety_gates_passed": safety_passed,
            "safety_gate_reason": gate_reason,
            "recommended_decision": decision,
            "score_breakdown": {
                "evidence_score": evidence_score,
                "rule_certainty": rule_certainty,
                "classification_score": classification_score,
                "ai_score": bounded_ai_score
            }
        }

confidence_engine = ConfidenceEngine()
