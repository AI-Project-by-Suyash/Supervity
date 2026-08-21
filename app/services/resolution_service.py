import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.exception import ExceptionRecord, ExceptionStatus
from app.models.resolution import ResolutionRecord, AllowedAction
from app.models.audit import ActorType
from app.services.confidence_engine import confidence_engine
from app.services.audit_service import AuditService
from app.repositories.exception_repository import ExceptionRepository

class ResolutionService:
    def __init__(self, db: Session):
        self.db = db
        self.exc_repo = ExceptionRepository(db)
        self.audit_service = AuditService(db)

    def execute_auto_resolve(self, exception_id: str) -> Dict[str, Any]:
        exc = self.exc_repo.get_by_id(exception_id)
        if not exc:
            raise HTTPException(status_code=404, detail="Exception not found")

        if exc.status == ExceptionStatus.RESOLVED:
            raise HTTPException(status_code=400, detail="Exception is already resolved.")

        evidence = json.loads(exc.evidence_json) if exc.evidence_json else {}
        conf_eval = confidence_engine.calculate_confidence(exc.type.value, evidence, ai_score=0.95)

        # Safety Gate Check
        if not conf_eval["safety_gates_passed"] or conf_eval["confidence"] < 0.90:
            self.audit_service.log_event(
                exception_id=exc.id,
                actor=ActorType.SYSTEM,
                action="AUTO_RESOLUTION_BLOCKED",
                reason=f"Policy block: Confidence {conf_eval['confidence']*100:.1f}% or safety gate failure: {conf_eval['safety_gate_reason']}",
                metadata=conf_eval
            )
            # Transition to PENDING_HUMAN if confidence 70-89% AND safety passed, else ESCALATED
            if conf_eval["safety_gates_passed"] and conf_eval["confidence"] >= 0.70:
                new_status = ExceptionStatus.PENDING_HUMAN
            else:
                new_status = ExceptionStatus.ESCALATED

            self.exc_repo.update_status(exc.id, new_status)
            raise HTTPException(
                status_code=400,
                detail=f"Auto-resolution blocked. Confidence {conf_eval['confidence']*100:.1f}% < 90% or safety gate failed. Routed to {new_status.value}."
            )

        # Execute Auto-Resolution
        exc.status = ExceptionStatus.RESOLVED
        exc.resolved_at = datetime.now(timezone.utc)

        # Persist Resolution record
        resolution = ResolutionRecord(
            id=f"RES-{uuid.uuid4().hex[:8].upper()}",
            exception_id=exc.id,
            suggested_action=AllowedAction.REQUEST_VENDOR_CORRECTION,
            reason="Autonomous resolution executed under verified safety gates and >90% confidence policy.",
            confidence=conf_eval["confidence"],
            score_breakdown=json.dumps(conf_eval["score_breakdown"]),
            safety_gates_passed=True,
            execution_mode="AUTO",
            executed_by="SYSTEM"
        )
        self.db.add(resolution)

        # Audit Event
        self.audit_service.log_event(
            exception_id=exc.id,
            actor=ActorType.SYSTEM,
            action="AUTO_RESOLVED",
            reason="Autonomous resolution executed under verified policy thresholds.",
            metadata={"confidence": conf_eval["confidence"], "action": "AUTO_RESOLVE"}
        )

        self.db.commit()
        return {
            "status": "RESOLVED",
            "exception_id": exc.id,
            "action_executed": "AUTO_RESOLVE",
            "actor": "SYSTEM",
            "message": "Exception successfully auto-resolved."
        }

    def execute_human_review(self, exception_id: str, decision: str, reason: str) -> Dict[str, Any]:
        exc = self.exc_repo.get_by_id(exception_id)
        if not exc:
            raise HTTPException(status_code=404, detail="Exception not found")

        decision = decision.upper()
        if decision not in ["APPROVE", "REJECT", "ESCALATE"]:
            raise HTTPException(status_code=400, detail="Invalid review decision. Must be APPROVE, REJECT, or ESCALATE.")

        if decision == "APPROVE":
            exc.status = ExceptionStatus.RESOLVED
            exc.resolved_at = datetime.now(timezone.utc)
            audit_action = "HUMAN_APPROVED"
        elif decision == "REJECT":
            exc.status = ExceptionStatus.REJECTED
            audit_action = "HUMAN_REJECTED"
        else:
            exc.status = ExceptionStatus.ESCALATED
            audit_action = "ESCALATED"

        self.audit_service.log_event(
            exception_id=exc.id,
            actor=ActorType.HUMAN_REVIEWER,
            action=audit_action,
            reason=reason,
            metadata={"reviewer_decision": decision}
        )

        self.db.commit()
        return {
            "status": exc.status.value,
            "exception_id": exc.id,
            "decision": decision,
            "actor": "HUMAN_REVIEWER"
        }
