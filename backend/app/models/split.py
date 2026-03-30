from sqlalchemy import Column, Numeric, Integer, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Split(Base):
    __tablename__ = "splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount_owed = Column(Numeric(12, 2), nullable=True) # Computed; nullable until final
    percentage = Column(Numeric(7, 2), nullable=True) # For PERCENTAGE splits
    share = Column(Integer, nullable=True) # For SHARE splits
    is_settled = Column(Boolean(), default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    expense = relationship("Expense", back_populates="splits")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_splits_expense_user"),
    )
