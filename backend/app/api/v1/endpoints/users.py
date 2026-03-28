"""
users.py — User management endpoints
  POST /users/          → Create user (internal, prefer /register)
  GET  /users/me        → Get current user profile
  PUT  /users/me        → Update current user profile
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    db_user = User(
        email=user_in.email,
        hashed_password=pwd_context.hash(user_in.password),
        full_name=user_in.full_name,
        preferred_currency=user_in.preferred_currency.upper(),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return current_user


@router.put("/me", response_model=UserResponse, summary="Update current user profile")
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.preferred_currency is not None:
        current_user.preferred_currency = user_in.preferred_currency.upper()
    if user_in.password is not None:
        current_user.hashed_password = pwd_context.hash(user_in.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
