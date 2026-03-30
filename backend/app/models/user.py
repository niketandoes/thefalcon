from sqlalchemy import Column, String, Boolean, DateTime, CHAR, func, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT
import uuid
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(CITEXT, nullable=False, unique=True, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(CHAR(60), nullable=False)
    preferred_currency = Column(CHAR(3), nullable=False, default="USD", server_default="USD")
    is_active = Column(Boolean(), default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
