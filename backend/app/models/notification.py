from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.db.base import Base

class NotificationType(str, enum.Enum):
    GROUP_INVITE = "GROUP_INVITE"
    EXPENSE_ADDED = "EXPENSE_ADDED"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_REMINDER = "PAYMENT_REMINDER"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SAEnum(NotificationType, name="notification_type"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean(), default=False, server_default="false")
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL"), nullable=True, index=True)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
