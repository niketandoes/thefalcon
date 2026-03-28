import uuid
from sqlalchemy import Column, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Split(Base):
    __tablename__ = "splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # EXACT amount this user owes for this expense (Calculated)
    amount_owed = Column(Numeric(10, 2), nullable=False)

    # Optional fields based on SplitType (Used for UI state recreation/validation)
    percentage = Column(Numeric(5, 2), nullable=True) # e.g. 50.00 (%)
    share = Column(Integer, nullable=True)            # e.g. 2 (shares)

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="splits")
