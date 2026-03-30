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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    """Create a signed JWT with an expiry claim."""
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/login/access-token",
    response_model=Token,
    summary="OAuth2 login",
)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Authenticate with email + password, receive a Bearer JWT."""
    result = await db.execute(
        select(User).filter(User.email == form_data.username)
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

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
    # Check for existing email
    existing = await db.execute(
        select(User).filter(User.email == user_in.email)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        preferred_currency=user_in.preferred_currency,
        is_active=True,
    )
    db.add(user)
    await db.flush() # assign user.id

    # Claim any pending group invites for this email
    from sqlalchemy import update
    from app.models.group_member import GroupMember
    await db.execute(
        update(GroupMember)
        .where(GroupMember.invited_email == user_in.email)
        .values(user_id=user.id)
    )

    await db.commit()
    await db.refresh(user)
    return user