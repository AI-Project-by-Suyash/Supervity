import json
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.audit import AuditEventRecord, ActorType
from app.repositories.audit_repository import AuditRepository

class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditRepository(db)

    def log_event(
        self,
        exception_id: str,
        actor: ActorType,
        action: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEventRecord:
        event = AuditEventRecord(
            id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            exception_id=exception_id,
            actor=actor,
            action=action,
            reason=reason,
            metadata_json=json.dumps(metadata or {})
        )
        return self.repo.create(event)

    def get_trail(self, exception_id: str) -> List[Dict[str, Any]]:
        records = self.repo.list_by_exception_id(exception_id)
        results = []
        for r in records:
            results.append({
                "id": r.id,
                "exception_id": r.exception_id,
                "actor": r.actor.value,
                "action": r.action,
                "reason": r.reason,
                "metadata": json.loads(r.metadata_json) if r.metadata_json else {},
                "timestamp": r.timestamp.isoformat()
            })
        return results
