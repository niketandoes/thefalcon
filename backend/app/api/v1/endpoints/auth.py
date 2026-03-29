"""
auth.py — Authentication endpoints
  POST /login/access-token  → OAuth2 password flow, returns JWT
  POST /register            → Register a new user (convenience alias)
"""
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    pass

@router.post('/login/access-token', response_model=Token, summary='OAuth2 login')
async def login_access_token(db: AsyncSession=Depends(deps.get_db), form_data: OAuth2PasswordRequestForm=Depends()) -> Any:
    """Authenticate with email + password, receive a Bearer JWT."""
    pass

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary='Register a new user')
async def register_user(*, db: AsyncSession=Depends(deps.get_db), user_in: UserCreate) -> Any:
    """
    Register a new account.
    Stores: name, email, hashed password, preferred_currency.
    """
    pass