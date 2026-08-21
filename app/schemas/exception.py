from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.exception import ExceptionType, Severity, ExceptionStatus

class EvidenceField(BaseModel):
    name: str
    value: Any
    source: str
    label: Optional[str] = None

class EvidenceModel(BaseModel):
    fields: List[EvidenceField]
    completeness_score: float = 1.0

class ExceptionSummary(BaseModel):
    id: str
    transaction_id: str
    reference_number: str
    vendor: str
    type: ExceptionType
    severity: Severity
    status: ExceptionStatus
    title: str
    difference: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExceptionDetail(BaseModel):
    id: str
    transaction_id: str
    transaction: Optional[Dict[str, Any]] = None
    type: ExceptionType
    severity: Severity
    status: ExceptionStatus
    title: str
    description: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    difference: Optional[str] = None
    threshold: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    resolution: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
