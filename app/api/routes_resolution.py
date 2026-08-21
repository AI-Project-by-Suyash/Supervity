from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.exception_repository import ExceptionRepository
from app.services.ai_service import AIService
from app.services.resolution_service import ResolutionService
from app.schemas.resolution import ResolveRequest, ResolveResponse, HumanReviewRequest, HumanReviewResponse
from app.schemas.ai import ExplanationResponse, SuggestionResponse

router = APIRouter()

@router.post('/exceptions/{exception_id}/explain', response_model=ExplanationResponse)
async def explain_exception(exception_id: str, db: Session = Depends(get_db)):
    repo = ExceptionRepository(db)
    exc = repo.get_by_id(exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    ai_service = AIService(db)
    return await ai_service.generate_explanation(exc)

@router.post('/exceptions/{exception_id}/suggest', response_model=SuggestionResponse)
async def suggest_resolution(exception_id: str, db: Session = Depends(get_db)):
    repo = ExceptionRepository(db)
    exc = repo.get_by_id(exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    ai_service = AIService(db)
    return await ai_service.generate_suggestion(exc)

@router.post('/exceptions/{exception_id}/resolve', response_model=ResolveResponse)
def resolve_exception(exception_id: str, payload: ResolveRequest, db: Session = Depends(get_db)):
    service = ResolutionService(db)
    return service.execute_auto_resolve(exception_id)

@router.post('/exceptions/{exception_id}/review', response_model=HumanReviewResponse)
def review_exception(exception_id: str, payload: HumanReviewRequest, db: Session = Depends(get_db)):
    service = ResolutionService(db)
    return service.execute_human_review(exception_id, payload.decision, payload.reason)
