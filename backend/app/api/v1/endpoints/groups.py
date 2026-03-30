"""
groups.py — Group management endpoints
  POST   /groups/                    → Create group
  GET    /groups/                    → List user's groups
  GET    /groups/{group_id}          → Group detail + members
  POST   /groups/{group_id}/invite   → Invite member by email (pending state)
  POST   /groups/{group_id}/members  → Add member by email (legacy, direct add)
  DELETE /groups/{group_id}/leave    → Leave group (enforces zero-balance guard)
  GET    /groups/{group_id}/balances → Simplified debt transactions
"""
from decimal import Decimal
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.algorithms.debt_simplifier import simplify_debts
from app.models.expense import Expense
from app.models.group import Group
from app.models.group_member import GroupMember, MemberStatus
from app.models.split import Split
from app.models.user import User
from app.schemas.expense import DebtSummary
from app.schemas.group import GroupCreate, GroupDetailResponse, GroupMemberDetailResponse, GroupResponse
from app.schemas.user import GroupMemberResponse
from app.services.notification_service import notify_group_invite

router = APIRouter()


# ---------------------------------------------------------------------------
# Request body schemas local to this router
# ---------------------------------------------------------------------------

class InviteMemberPayload(PydanticBaseModel):
    email: str


class AddMemberPayload(PydanticBaseModel):
    email: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_group_or_404(
    group_id: UUID, db: AsyncSession
) -> Group:
    result = await db.execute(select(Group).filter(Group.id == group_id))
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


async def _require_membership(
    group_id: UUID, user_id: UUID, db: AsyncSession
) -> GroupMember:
    """Ensure the user is an accepted member of the group."""
    result = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.status == MemberStatus.ACCEPTED,
        )
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this group")
    return member


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new group",
)
async def create_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    group_in: GroupCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new expense group and auto-add the creator as the first
    accepted member.
    """
    group = Group(
        name=group_in.name,
        description=group_in.description,
        created_by=current_user.id,
    )
    db.add(group)
    await db.flush()  # assigns group.id

    membership = GroupMember(
        user_id=current_user.id,
        group_id=group.id,
        status=MemberStatus.ACCEPTED,
        role="admin",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(group)
    return group


@router.get(
    "/",
    response_model=List[GroupResponse],
    summary="List current user's groups",
)
async def read_groups(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Return all groups where the current user is an accepted member."""
    result = await db.execute(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(
            GroupMember.user_id == current_user.id,
            GroupMember.status == MemberStatus.ACCEPTED,
        )
        .order_by(Group.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{group_id}",
    response_model=GroupDetailResponse,
    summary="Get group detail with members",
)
async def get_group_detail(
    group_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Return group metadata and the full member list (including pending invites).
    Only accessible to accepted members.
    """
    await _require_membership(group_id, current_user.id, db)

    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .filter(Group.id == group_id)
    )
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members = []
    for m in group.members:
        if m.user:
            members.append(
                GroupMemberDetailResponse(
                    user_id=m.user.id,
                    full_name=m.user.full_name,
                    email=m.user.email,
                    preferred_currency=m.user.preferred_currency,
                    status=m.status,
                )
            )
        else:
            members.append(
                GroupMemberDetailResponse(
                    user_id=None,
                    full_name=None,
                    email=m.invited_email,
                    preferred_currency="USD",
                    status=m.status,
                )
            )

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=group.created_at,
        members=members,
    )


@router.post(
    "/{group_id}/invite",
    status_code=status.HTTP_201_CREATED,
    summary="Invite a member to a group by email (pending state)",
)
async def invite_member(
    group_id: UUID,
    payload: InviteMemberPayload,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Send a group invite to a registered user by email.
    The membership is created in PENDING status.
    A GROUP_INVITE notification is sent to the invitee.
    """
    await _require_membership(group_id, current_user.id, db)
    group = await _get_group_or_404(group_id, db)

    # Find the invitee by email
    result = await db.execute(select(User).filter(User.email == payload.email))
    invitee = result.scalars().first()
    
    if invitee and invitee.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot invite yourself")

    # Check if a pending invite or active membership exists
    if invitee:
        existing_result = await db.execute(
            select(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == invitee.id
            )
        )
    else:
        existing_result = await db.execute(
            select(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.invited_email == payload.email
            )
        )
    existing_member = existing_result.scalars().first()

    if existing_member:
        if existing_member.status == MemberStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="User is already a member")
        
        # If REJECTED or PENDING, allow re-invite by resetting to PENDING
        existing_member.status = MemberStatus.PENDING
        existing_member.invited_by = current_user.id
        existing_member.invited_email = payload.email
        if invitee:
            existing_member.user_id = invitee.id
    else:
        pending_member = GroupMember(
            user_id=invitee.id if invitee else None,
            group_id=group_id,
            status=MemberStatus.PENDING,
            invited_by=current_user.id,
            invited_email=payload.email,
        )
        db.add(pending_member)

    # Fire notification to the app if they have an account
    # If they don't have an account, you would normally send an external email here.
    if invitee:
        await notify_group_invite(
            db,
            invitee_id=invitee.id,
            inviter_name=current_user.full_name or current_user.email,
            group_id=group_id,
            group_name=group.name,
        )

    await db.commit()
    return {"detail": f"Invite sent to {payload.email}"}


@router.post(
    "/{group_id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to a group by email (direct add)",
)
async def add_member(
    group_id: UUID,
    payload: AddMemberPayload,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Legacy endpoint — directly adds a member as ACCEPTED (no invite flow).
    Kept for backwards compatibility; prefer POST /{group_id}/invite.
    """
    await _require_membership(group_id, current_user.id, db)

    result = await db.execute(select(User).filter(User.email == payload.email))
    target_user = result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="No user found with that email")

    existing = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == target_user.id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="User is already a member or has a pending invite")

    membership = GroupMember(
        user_id=target_user.id,
        group_id=group_id,
        status=MemberStatus.ACCEPTED,
    )
    db.add(membership)
    await db.commit()
    return {"detail": f"{payload.email} added to the group"}


@router.delete(
    "/{group_id}/leave",
    status_code=status.HTTP_200_OK,
    summary="Leave a group (blocked if balance is non-zero)",
)
async def leave_group(
    group_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Remove the current user from the group.
    Blocked if the user has an outstanding non-zero balance in the group.
    """
    membership = await _require_membership(group_id, current_user.id, db)

    # ── Zero-balance guard ────────────────────────────────────────────────
    # Compute net balance for the leaving user inside this group.
    expenses_result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .filter(Expense.group_id == group_id)
    )
    expenses = expenses_result.scalars().all()

    net_balance = Decimal("0")
    user_id_str = str(current_user.id)

    for expense in expenses:
        if expense.payer_id == current_user.id:
            # Others owe me (total - my own split)
            for s in expense.splits:
                if s.user_id != current_user.id:
                    net_balance += s.amount_owed
        for s in expense.splits:
            if s.user_id == current_user.id and expense.payer_id != current_user.id:
                net_balance -= s.amount_owed

    if abs(net_balance) > Decimal("0.01"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot leave: you have an outstanding balance of {net_balance:.2f}",
        )

    await db.delete(membership)
    await db.commit()
    return {"detail": "You have left the group"}


@router.get(
    "/{group_id}/balances",
    response_model=List[DebtSummary],
    summary="Get simplified debt transactions for a group",
)
async def get_group_balances(
    group_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Compute net balances for all members in the group, then run the
    debt-simplification algorithm to return the minimal set of transfers.
    """
    await _require_membership(group_id, current_user.id, db)

    # Fetch all expenses in this group with their splits
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .filter(Expense.group_id == group_id)
    )
    expenses = result.scalars().all()

    # Build net-balance map:  positive = owed money, negative = owes money
    balances: dict[str, Decimal] = {}

    for expense in expenses:
        payer_id = str(expense.payer_id)

        for split in expense.splits:
            uid = str(split.user_id)
            if uid == payer_id:
                # The payer is also in the split — they owe themselves, net zero
                # but they are credited the full amount and debited their share
                continue

            # Debtor owes money
            balances[uid] = balances.get(uid, Decimal("0")) - split.amount_owed
            # Creditor is owed money
            balances[payer_id] = balances.get(payer_id, Decimal("0")) + split.amount_owed

    return simplify_debts(balances)