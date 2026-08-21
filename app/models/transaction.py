from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    reference_number: Mapped[str] = mapped_column(String(64), index=True)
    transaction_type: Mapped[str] = mapped_column(String(32))
    vendor: Mapped[str] = mapped_column(String(128), index=True)
    expected_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    due_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    reference_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default='INR')
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    exceptions = relationship('ExceptionRecord', back_populates='transaction', cascade='all, delete-orphan')
