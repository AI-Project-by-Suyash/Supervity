import json
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.exception import ExceptionRecord
from app.models.audit import ActorType
from app.llm.provider import llm_provider
from app.llm.prompts import SYSTEM_PROMPT, build_explain_prompt, build_suggest_prompt
from app.services.confidence_engine import confidence_engine
from app.services.audit_service import AuditService

class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    async def generate_explanation(self, exc: ExceptionRecord) -> Dict[str, Any]:
        evidence = json.loads(exc.evidence_json) if exc.evidence_json else {}
        exc_dict = {
            "type": exc.type.value,
            "severity": exc.severity.value,
            "description": exc.description,
            "expected_value": exc.expected_value,
            "actual_value": exc.actual_value,
            "difference": exc.difference,
            "threshold": exc.threshold
        }

        user_prompt = build_explain_prompt(exc_dict, evidence)
        ai_resp = await llm_provider.generate_json(SYSTEM_PROMPT, user_prompt)

        # Audit Event
        self.audit_service.log_event(
            exception_id=exc.id,
            actor=ActorType.AI_EMPLOYEE,
            action="AI_EXPLANATION_GENERATED",
            reason=ai_resp.get("explanation"),
            metadata={
                "provider": ai_resp.get("provider_used"),
                "cited_fields": ai_resp.get("evidence_fields", [])
            }
        )

        return {
            "explanation": ai_resp.get("explanation", "Discrepancy analyzed against verified evidence."),
            "evidence_fields": ai_resp.get("evidence_fields", []),
            "provider_used": ai_resp.get("provider_used", "AI Employee")
        }

    async def generate_suggestion(self, exc: ExceptionRecord) -> Dict[str, Any]:
        evidence = json.loads(exc.evidence_json) if exc.evidence_json else {}
        exc_dict = {
            "type": exc.type.value,
            "severity": exc.severity.value,
            "description": exc.description,
            "expected_value": exc.expected_value,
            "actual_value": exc.actual_value,
            "difference": exc.difference
        }

        user_prompt = build_suggest_prompt(exc_dict, evidence)
        ai_resp = await llm_provider.generate_json(SYSTEM_PROMPT, user_prompt)

        raw_ai_score = float(ai_resp.get("ai_score", 0.90))
        confidence_result = confidence_engine.calculate_confidence(
            exception_type=exc.type.value,
            evidence_data=evidence,
            ai_score=raw_ai_score
        )

        # Audit Event
        self.audit_service.log_event(
            exception_id=exc.id,
            actor=ActorType.AI_EMPLOYEE,
            action="AI_RECOMMENDATION_GENERATED",
            reason=ai_resp.get("reason"),
            metadata={
                "suggested_action": ai_resp.get("suggested_action"),
                "confidence": confidence_result["confidence"],
                "provider": ai_resp.get("provider_used"),
                "decision": confidence_result["recommended_decision"]
            }
        )

        return {
            "suggested_action": ai_resp.get("suggested_action", "ESCALATE_TO_HUMAN"),
            "reason": ai_resp.get("reason", "Recommendation evaluated against policy rules."),
            "confidence": confidence_result["confidence"],
            "score_breakdown": confidence_result["score_breakdown"],
            "safety_gates_passed": confidence_result["safety_gates_passed"],
            "recommended_decision": confidence_result["recommended_decision"],
            "provider_used": ai_resp.get("provider_used", "AI Employee")
        }
