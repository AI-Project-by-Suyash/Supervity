from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.resolution import AllowedAction

class ResolutionCreate(BaseModel):
    suggested_action: AllowedAction
    reason: str
    confidence: float
    score_breakdown: Dict[str, float]
    safety_gates_passed: bool
    execution_mode: str = 'AUTO'
    executed_by: str = 'SYSTEM'

class ResolveRequest(BaseModel):
    mode: str = 'AUTO'

class ResolveResponse(BaseModel):
    status: str
    exception_id: str
    action_executed: str
    actor: str
    message: str

class HumanReviewRequest(BaseModel):
    decision: str  # APPROVE, REJECT, ESCALATE
    reason: str

class HumanReviewResponse(BaseModel):
    status: str
    exception_id: str
    decision: str
    actor: str
