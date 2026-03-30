from sqlalchemy import Column, Numeric, String, SMALLINT, ForeignKey, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    split_id = Column(UUID(as_uuid=True), ForeignKey("splits.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    quantity = Column(SMALLINT, nullable=False, default=1, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
