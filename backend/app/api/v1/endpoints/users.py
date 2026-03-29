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
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(*, db: AsyncSession=Depends(deps.get_db), user_in: UserCreate) -> Any:
    pass

@router.get('/me', response_model=UserResponse, summary='Get current user')
async def read_user_me(current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.put('/me', response_model=UserResponse, summary='Update current user profile')
async def update_user_me(*, db: AsyncSession=Depends(deps.get_db), user_in: UserUpdate, current_user: User=Depends(deps.get_current_user)) -> Any:
    pass