from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .user import UserResponse

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: UUID
    created_at: datetime
    
    # We can choose to include members in the response later
    # members: List[UserResponse] = []

    class Config:
        from_attributes = True
