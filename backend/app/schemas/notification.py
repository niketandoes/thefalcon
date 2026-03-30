from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Single notification item returned to the client."""
    id: UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool
    group_id: Optional[UUID] = None
    expense_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    """Paginated wrapper for notification listing."""
    total: int
    unread_count: int
    items: List[NotificationResponse]


class InviteActionRequest(BaseModel):
    """Payload for accepting or rejecting a group invite."""
    action: str  # "accept" or "reject"
