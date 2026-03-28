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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Helper ────────────────────────────────────────────────────────────────────

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login/access-token", response_model=Token, summary="OAuth2 login")
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Authenticate with email + password, receive a Bearer JWT."""
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new account.
    Stores: name, email, hashed password, preferred_currency.
    """
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

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
