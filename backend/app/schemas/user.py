from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    preferred_currency: str = Field(default="USD", min_length=3, max_length=3)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    preferred_currency: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Used in members list responses
class GroupMemberResponse(BaseModel):
    user_id: UUID
    full_name: Optional[str]
    email: str
    preferred_currency: str

    class Config:
        from_attributes = True
