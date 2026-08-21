from datetime import datetime, timezone
from typing import Optional
import enum
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ActorType(str, enum.Enum):
    SYSTEM = 'SYSTEM'
    AI_EMPLOYEE = 'AI_EMPLOYEE'
    HUMAN_REVIEWER = 'HUMAN_REVIEWER'

class AuditEventRecord(Base):
    __tablename__ = 'audit_events'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    exception_id: Mapped[str] = mapped_column(String(64), ForeignKey('exceptions.id'), index=True)
    actor: Mapped[ActorType] = mapped_column(Enum(ActorType))
    action: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    exception = relationship('ExceptionRecord', back_populates='audit_events')
