import enum
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    description = Column(String, nullable=False)
    split_type = Column(SQLEnum(SplitType), nullable=False)
    expense_date = Column(Date, nullable=False, default=date.today)

    # Recurring fields
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(SQLEnum(RecurringFrequency), nullable=True)
    recurring_day_of_week = Column(Integer, nullable=True)   # 0=Sunday … 6=Saturday
    recurring_day_of_month = Column(Integer, nullable=True)  # 1-31

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid")
    splits = relationship("Split", back_populates="expense", cascade="all, delete-orphan")
