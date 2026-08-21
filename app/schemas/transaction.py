from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class TransactionBase(BaseModel):
    id: str
    reference_number: str
    transaction_type: str
    vendor: str
    expected_amount: Optional[float] = None
    actual_amount: Optional[float] = None
    expected_quantity: Optional[int] = None
    actual_quantity: Optional[int] = None
    due_date: Optional[str] = None
    reference_date: Optional[str] = None
    currency: str = 'INR'
    metadata_json: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
