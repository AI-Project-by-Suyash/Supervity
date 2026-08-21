import pytest
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.seed.seed_data import seed_database
from app.services.resolution_service import ResolutionService
from app.models.exception import ExceptionRecord, ExceptionStatus
from fastapi import HTTPException



def test_auto_resolve_high_confidence_success():
    db = SessionLocal()
    try:
        service = ResolutionService(db)
        # EXC-1001 is High confidence (25% variance, complete evidence)
        resp = service.execute_auto_resolve("EXC-1001")
        assert resp["status"] == "RESOLVED"
        assert resp["action_executed"] == "AUTO_RESOLVE"

        # Verify DB status
        exc = db.query(ExceptionRecord).filter(ExceptionRecord.id == "EXC-1001").first()
        assert exc.status == ExceptionStatus.RESOLVED
        assert exc.resolved_at is not None
    finally:
        db.close()

def test_auto_resolve_blocked_on_missing_evidence():
    db = SessionLocal()
    try:
        service = ResolutionService(db)
        # EXC-2001 has missing receipt quantity (<70% completeness)
        with pytest.raises(HTTPException) as exc_info:
            service.execute_auto_resolve("EXC-2001")
        assert exc_info.value.status_code == 400
        assert "Auto-resolution blocked" in exc_info.value.detail

        # Verify routed to ESCALATED
        exc = db.query(ExceptionRecord).filter(ExceptionRecord.id == "EXC-2001").first()
        assert exc.status == ExceptionStatus.ESCALATED
    finally:
        db.close()

def test_human_review_approval():
    db = SessionLocal()
    try:
        service = ResolutionService(db)
        resp = service.execute_human_review(
            exception_id="EXC-3001",
            decision="APPROVE",
            reason="AP terms verified with vendor and approved by finance director."
        )
        assert resp["status"] == "RESOLVED"
        assert resp["decision"] == "APPROVE"

        exc = db.query(ExceptionRecord).filter(ExceptionRecord.id == "EXC-3001").first()
        assert exc.status == ExceptionStatus.RESOLVED
    finally:
        db.close()
