from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import GroupMemberResponse
from app.models.group_member import MemberStatus


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupResponse(GroupBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class GroupMemberDetailResponse(BaseModel):
    """Member detail including invite status."""
    user_id: Optional[UUID] = None
    full_name: Optional[str] = None
    email: str
    preferred_currency: str
    status: MemberStatus

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupBase):
    """Full group detail including members list."""
    id: UUID
    created_at: datetime
    members: List[GroupMemberDetailResponse] = []

    class Config:
        from_attributes = True
