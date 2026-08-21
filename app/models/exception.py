from datetime import datetime, timezone
from typing import Optional
import enum
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ExceptionType(str, enum.Enum):
    AMOUNT_MISMATCH = 'AMOUNT_MISMATCH'
    QUANTITY_MISMATCH = 'QUANTITY_MISMATCH'
    PAYMENT_OVERDUE = 'PAYMENT_OVERDUE'

class Severity(str, enum.Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

class ExceptionStatus(str, enum.Enum):
    OPEN = 'OPEN'
    ANALYZING = 'ANALYZING'
    RECOMMENDED = 'RECOMMENDED'
    PENDING_HUMAN = 'PENDING_HUMAN'
    RESOLVED = 'RESOLVED'
    ESCALATED = 'ESCALATED'
    REJECTED = 'REJECTED'

class ExceptionRecord(Base):
    __tablename__ = 'exceptions'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), ForeignKey('transactions.id'), index=True)
    type: Mapped[ExceptionType] = mapped_column(Enum(ExceptionType))
    severity: Mapped[Severity] = mapped_column(Enum(Severity), index=True)
    status: Mapped[ExceptionStatus] = mapped_column(Enum(ExceptionStatus), default=ExceptionStatus.OPEN, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    expected_value: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    actual_value: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    difference: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    threshold: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    transaction = relationship('Transaction', back_populates='exceptions')
    resolutions = relationship('ResolutionRecord', back_populates='exception', cascade='all, delete-orphan')
    audit_events = relationship('AuditEventRecord', back_populates='exception', cascade='all, delete-orphan')
