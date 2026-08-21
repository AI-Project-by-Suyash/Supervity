from datetime import datetime, timezone
import enum
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AllowedAction(str, enum.Enum):
    REQUEST_VENDOR_CORRECTION = 'REQUEST_VENDOR_CORRECTION'
    REQUEST_PAYMENT_REVIEW = 'REQUEST_PAYMENT_REVIEW'
    REQUEST_QUANTITY_REVIEW = 'REQUEST_QUANTITY_REVIEW'
    APPROVE_EXCEPTION = 'APPROVE_EXCEPTION'
    ESCALATE_TO_HUMAN = 'ESCALATE_TO_HUMAN'
    NO_ACTION = 'NO_ACTION'

class ResolutionRecord(Base):
    __tablename__ = 'resolutions'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    exception_id: Mapped[str] = mapped_column(String(64), ForeignKey('exceptions.id'), index=True)
    suggested_action: Mapped[AllowedAction] = mapped_column(Enum(AllowedAction))
    reason: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    score_breakdown: Mapped[str] = mapped_column(Text)
    safety_gates_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    execution_mode: Mapped[str] = mapped_column(String(32), default='AUTO')
    executed_by: Mapped[str] = mapped_column(String(64), default='SYSTEM')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    exception = relationship('ExceptionRecord', back_populates='resolutions')
