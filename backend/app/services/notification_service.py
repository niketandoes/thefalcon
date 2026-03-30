"""
notification_service.py
========================
Centralised helper for creating notifications.

All notification side-effects should route through this module so that
future enhancements (WebSocket push, email digest, etc.) only need to be
wired in one place.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    type: NotificationType,
    title: str,
    message: str,
    group_id: Optional[UUID] = None,
    expense_id: Optional[UUID] = None,
) -> Notification:
    """
    Persist a notification row and return it.

    Parameters
    ----------
    db : AsyncSession
    user_id : UUID            – the recipient
    type : NotificationType   – GROUP_INVITE | EXPENSE_ADDED | ...
    title : str               – short headline shown in the notification bell
    message : str             – longer body text
    group_id : UUID, optional – deep-link reference
    expense_id : UUID, optional – deep-link reference

    Returns
    -------
    Notification  – the ORM instance (already flushed, not yet committed;
                    caller controls the transaction boundary).
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        group_id=group_id,
        expense_id=expense_id,
    )
    db.add(notification)
    await db.flush()
    return notification


async def notify_group_invite(
    db: AsyncSession,
    *,
    invitee_id: UUID,
    inviter_name: str,
    group_id: UUID,
    group_name: str,
) -> Notification:
    """Fire a GROUP_INVITE notification to the invitee."""
    return await create_notification(
        db,
        user_id=invitee_id,
        type=NotificationType.GROUP_INVITE,
        title="Group Invitation",
        message=f"{inviter_name} invited you to join '{group_name}'.",
        group_id=group_id,
    )


async def notify_expense_tagged(
    db: AsyncSession,
    *,
    tagged_user_id: UUID,
    payer_name: str,
    expense_description: str,
    amount_owed: str,
    group_id: UUID,
    expense_id: UUID,
) -> Notification:
    """Fire an EXPENSE_ADDED notification when a user is tagged in a split."""
    return await create_notification(
        db,
        user_id=tagged_user_id,
        type=NotificationType.EXPENSE_ADDED,
        title="New Expense",
        message=f"{payer_name} added '{expense_description}' — you owe {amount_owed}.",
        group_id=group_id,
        expense_id=expense_id,
    )
