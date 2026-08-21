from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.audit import ActorType

class AuditEventRead(BaseModel):
    id: str
    exception_id: str
    actor: ActorType
    action: str
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
