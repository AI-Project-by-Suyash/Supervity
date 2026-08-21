from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.models.resolution import AllowedAction

class ExplanationResponse(BaseModel):
    explanation: str
    evidence_fields: List[str]
    provider_used: str

class SuggestionResponse(BaseModel):
    suggested_action: AllowedAction
    reason: str
    confidence: float
    score_breakdown: Dict[str, float]
    safety_gates_passed: bool
    recommended_decision: str
    provider_used: str
