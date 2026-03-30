from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, CITEXT
import enum
import uuid
from app.db.base import Base

class MemberStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    status = Column(SAEnum(MemberStatus, name="member_status"), nullable=False, default=MemberStatus.ACCEPTED, server_default="ACCEPTED")
    role = Column(String(20), nullable=False, default="member", server_default="member")
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invited_email = Column(CITEXT, nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    group = relationship("Group", back_populates="members", foreign_keys=[group_id])

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_gm_group_user"),
        UniqueConstraint("group_id", "invited_email", name="uq_gm_group_email"),
    )
