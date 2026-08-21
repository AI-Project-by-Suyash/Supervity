from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.audit_service import AuditService
from app.schemas.audit import AuditEventRead

router = APIRouter()

@router.get('/exceptions/{exception_id}/audit')
def get_exception_audit_trail(exception_id: str, db: Session = Depends(get_db)):
    service = AuditService(db)
    return service.get_trail(exception_id)
