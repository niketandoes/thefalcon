"""
groups.py — Group management endpoints
  POST   /groups/                  → Create group
  GET    /groups/                  → List user's groups
  GET    /groups/{group_id}        → Group detail + members
  POST   /groups/{group_id}/members → Add member by email
  DELETE /groups/{group_id}/leave  → Leave group (enforces zero-balance guard)
  GET    /groups/{group_id}/balances → Simplified debt transactions
"""

from decimal import Decimal
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.algorithms.debt_simplifier import simplify_debts
from app.models.expense import Expense
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.split import Split
from app.models.user import User
from app.schemas.expense import DebtSummary
from app.schemas.group import GroupCreate, GroupDetailResponse, GroupResponse
from app.schemas.user import GroupMemberResponse


router = APIRouter()


# ── Create ────────────────────────────────────────────────────────────────────

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
    group = Group(name=group_in.name, description=group_in.description)
    db.add(group)
    await db.flush()

    member = GroupMember(user_id=current_user.id, group_id=group.id)
    db.add(member)

    await db.commit()
    await db.refresh(group)
    return group


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[GroupResponse], summary="List current user's groups")
async def read_groups(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    query = (
        select(Group)
        .join(GroupMember)
        .filter(GroupMember.user_id == current_user.id)
    )
    result = await db.execute(query)
    return result.scalars().all()


# ── Detail ────────────────────────────────────────────────────────────────────

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
    # Verify membership
    membership = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not membership.scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this group")

    # Load group with members + their user details
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .filter(Group.id == group_id)
    )
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Build response
    members_out = [
        GroupMemberResponse(
            user_id=m.user_id,
            full_name=m.user.full_name,
            email=m.user.email,
            preferred_currency=m.user.preferred_currency,
        )
        for m in group.members
    ]

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=group.created_at,
        members=members_out,
    )


# ── Add Member ────────────────────────────────────────────────────────────────

class AddMemberPayload(PydanticBaseModel):
    email: str



@router.post(
    "/{group_id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to a group by email",
)
async def add_member(
    group_id: UUID,
    payload: AddMemberPayload,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Ensure requester is a member
    membership = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not membership.scalars().first():
        raise HTTPException(status_code=403, detail="Not a member of this group")

    # Find the user to add
    target = await db.execute(select(User).filter(User.email == payload.email))
    target_user = target.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check not already a member
    existing = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == target_user.id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="User is already a group member")

    db.add(GroupMember(user_id=target_user.id, group_id=group_id))
    await db.commit()
    return {"detail": f"{target_user.full_name or target_user.email} added to group"}


# ── Leave Group (with zero-balance guard) ─────────────────────────────────────

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
    # 1. Confirm membership
    membership_q = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    membership = membership_q.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="You are not a member of this group")

    # 2. Compute user's net balance in this group
    splits_q = await db.execute(
        select(Split).join(Expense).filter(Expense.group_id == group_id)
    )
    all_splits = splits_q.scalars().all()

    balance = Decimal("0")
    uid = str(current_user.id)

    for split in all_splits:
        payer_id = str(split.expense.payer_id)
        split_uid = str(split.user_id)
        if payer_id != split_uid:
            if payer_id == uid:
                balance += split.amount_owed
            if split_uid == uid:
                balance -= split.amount_owed

    # 3. Enforce zero-balance guard
    if abs(balance) >= Decimal("0.01"):
        direction = "owed to you" if balance > 0 else "you owe"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot leave group: ${abs(balance):.2f} is still {direction}. Settle all debts first.",
        )

    await db.delete(membership)
    await db.commit()
    return {"detail": "Successfully left the group"}


# ── Balances ──────────────────────────────────────────────────────────────────

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
    # Verify membership
    membership_q = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not membership_q.scalars().first():
        raise HTTPException(status_code=403, detail="Not a member of this group")

    splits_q = await db.execute(
        select(Split).join(Expense).filter(Expense.group_id == group_id)
    )
    all_splits = splits_q.scalars().all()

    balances: dict[str, Decimal] = {}
    for split in all_splits:
        payer_id = str(split.expense.payer_id)
        owed_uid = str(split.user_id)
        if payer_id != owed_uid:
            balances.setdefault(payer_id, Decimal("0"))
            balances.setdefault(owed_uid, Decimal("0"))
            balances[payer_id] += split.amount_owed
            balances[owed_uid] -= split.amount_owed

    return simplify_debts(balances)
