from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.exception import ExceptionRecord, ExceptionStatus, Severity, ExceptionType
from app.models.transaction import Transaction

class ExceptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, exception_id: str) -> Optional[ExceptionRecord]:
        return self.db.query(ExceptionRecord).filter(ExceptionRecord.id == exception_id).first()

    def list_with_filters(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        exception_type: Optional[str] = None
    ) -> List[ExceptionRecord]:
        query = self.db.query(ExceptionRecord).join(Transaction)
        if status:
            query = query.filter(ExceptionRecord.status == status)
        if severity:
            query = query.filter(ExceptionRecord.severity == severity)
        if exception_type:
            query = query.filter(ExceptionRecord.type == exception_type)
        return query.order_by(ExceptionRecord.created_at.desc()).all()

    def update_status(self, exception_id: str, new_status: ExceptionStatus) -> Optional[ExceptionRecord]:
        rec = self.get_by_id(exception_id)
        if rec:
            rec.status = new_status
            self.db.commit()
            self.db.refresh(rec)
        return rec

    def create(self, exception: ExceptionRecord) -> ExceptionRecord:
        self.db.add(exception)
        self.db.commit()
        self.db.refresh(exception)
        return exception
