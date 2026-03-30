from sqlalchemy import Column, Numeric, String, Text, DateTime, ForeignKey, Enum as SAEnum, func, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.db.base import Base

class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DISPUTED = "DISPUTED"
    CANCELLED = "CANCELLED"

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="RESTRICT"), nullable=False, index=True)
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    payee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(CHAR(3), nullable=False, default="USD", server_default="USD")
    status = Column(SAEnum(SettlementStatus, name="settlement_status"), nullable=False, default=SettlementStatus.PENDING, server_default="PENDING")
    payment_reference = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
