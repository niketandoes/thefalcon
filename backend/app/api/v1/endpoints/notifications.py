"""
notifications.py — Notification endpoints
  GET    /notifications/                 → List user's notifications
  PATCH  /notifications/{id}/read       → Mark a notification as read
  POST   /notifications/invites/{group_id}/respond → Accept or reject a group invite
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.group import Group
from app.models.group_member import GroupMember, MemberStatus
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.notification import InviteActionRequest, NotificationList, NotificationResponse

router = APIRouter()


@router.get(
    "/",
    response_model=NotificationList,
    summary="List notifications for the current user",
)
async def list_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Return paginated notifications ordered newest-first.
    Optionally filter to unread only.
    """
    base_filter = Notification.user_id == current_user.id
    if unread_only:
        base_filter = and_(base_filter, Notification.is_read == False)  # noqa: E712

    # Total count
    total_result = await db.execute(
        select(func.count(Notification.id)).filter(base_filter)
    )
    total = total_result.scalar_one()

    # Unread count (always)
    unread_result = await db.execute(
        select(func.count(Notification.id)).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    unread_count = unread_result.scalar_one()

    # Paginated items
    result = await db.execute(
        select(Notification)
        .filter(base_filter)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()

    return NotificationList(
        total=total,
        unread_count=unread_count,
        items=[NotificationResponse.model_validate(n) for n in items],
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Toggle a notification to read status."""
    result = await db.execute(
        select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


@router.post(
    "/invites/{group_id}/respond",
    status_code=status.HTTP_200_OK,
    summary="Accept or reject a group invite",
)
async def respond_to_invite(
    group_id: UUID,
    payload: InviteActionRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Accept or reject a pending group invite.

    Payload: { "action": "accept" | "reject" }

    On accept → membership status moves to ACCEPTED.
    On reject → membership status moves to REJECTED.
    In both cases, the corresponding GROUP_INVITE notification is marked as read.
    """
    action = payload.action.lower().strip()
    if action not in ("accept", "reject"):
        raise HTTPException(status_code=400, detail="action must be 'accept' or 'reject'")

    # Find the pending membership
    result = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.status == MemberStatus.PENDING,
        )
    )
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="No pending invite found for this group")

    if action == "accept":
        membership.status = MemberStatus.ACCEPTED
        detail_msg = "You have joined the group"
    else:
        membership.status = MemberStatus.REJECTED
        detail_msg = "Invite rejected"

    # Mark matching GROUP_INVITE notifications as read
    notif_result = await db.execute(
        select(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.GROUP_INVITE,
            Notification.group_id == group_id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    for notif in notif_result.scalars().all():
        notif.is_read = True

    await db.commit()
    return {"detail": detail_msg}
