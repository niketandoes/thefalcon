from sqlalchemy import Column, String, Numeric, Boolean, Date, DateTime, ForeignKey, Integer, SMALLINT, Enum as SAEnum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.db.base import Base

class SplitType(str, enum.Enum):
    EQUAL = "EQUAL"
    PERCENTAGE = "PERCENTAGE"
    SHARE = "SHARE"
    ITEM = "ITEM"

class RecurringFrequency(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    SEMI_MONTHLY = "SEMI_MONTHLY"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="RESTRICT"), nullable=False, index=True)
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, index=True)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD", server_default="USD")
    split_type = Column(SAEnum(SplitType, name="split_type"), nullable=False)
    expense_date = Column(Date, nullable=False, server_default=func.current_date())
    is_recurring = Column(Boolean(), default=False, server_default="false")
    recurring_frequency = Column(SAEnum(RecurringFrequency, name="recurring_frequency"), nullable=True)
    recurring_day_of_week = Column(SMALLINT, nullable=True)
    recurring_day_of_month = Column(SMALLINT, nullable=True)
    receipt_url = Column(String(), nullable=True)
    is_deleted = Column(Boolean(), default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    splits = relationship("Split", back_populates="expense", cascade="all, delete-orphan")
