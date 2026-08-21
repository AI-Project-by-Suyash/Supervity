from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditEventRecord

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event: AuditEventRecord) -> AuditEventRecord:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_by_exception_id(self, exception_id: str) -> List[AuditEventRecord]:
        return (
            self.db.query(AuditEventRecord)
            .filter(AuditEventRecord.exception_id == exception_id)
            .order_by(AuditEventRecord.timestamp.asc())
            .all()
        )
