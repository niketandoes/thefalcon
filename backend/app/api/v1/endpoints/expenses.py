"""
expenses.py — Expense tracking endpoints
  POST /expenses/                      → Log a new expense
  GET  /expenses/                      → List expenses (filterable by group_id)
  GET  /expenses/{expense_id}          → Get expense detail
  GET  /expenses/dashboard/stats       → Aggregated global stats for current user
  GET  /expenses/dashboard/stats/group/{group_id} → Stats filtered by group
"""

import decimal
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.expense import Expense, SplitType
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.split import Split
from app.models.user import User
from app.schemas.expense import (
    DashboardStats,
    ExpenseCreate,
    ExpenseResponse,
    GroupDebt,
)
from app.services.currency_service import convert_currency

router = APIRouter()


# ── Create Expense ────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a new expense with split calculation",
)
async def create_expense(
    *,
    db: AsyncSession = Depends(deps.get_db),
    expense_in: ExpenseCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Logs an expense. Accepts all split methods (EQUAL, PERCENTAGE, SHARE, ITEM)
    and optional recurring schedule flags.
    """
    # Verify user is a member of the group
    membership_q = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == expense_in.group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not membership_q.scalars().first():
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    # Determine actual payer (defaults to requester)
    payer_id = expense_in.payer_id or current_user.id

    # ── validate & route to the correct split algorithm ──────────────────────
    user_ids = []
    user_percentages: dict = {}
    user_shares: dict = {}
    user_exact_amounts: dict = {}

    for split in expense_in.splits:
        uid_str = str(split.user_id)

        if expense_in.split_type == SplitType.EQUAL:
            user_ids.append(uid_str)

        elif expense_in.split_type == SplitType.PERCENTAGE:
            if split.percentage is None:
                raise HTTPException(status_code=400, detail=f"Percentage missing for user {uid_str}")
            user_percentages[uid_str] = split.percentage

        elif expense_in.split_type == SplitType.SHARE:
            if split.share is None:
                raise HTTPException(status_code=400, detail=f"Share value missing for user {uid_str}")
            user_shares[uid_str] = split.share

        elif expense_in.split_type == SplitType.ITEM:
            if split.amount_owed is None:
                raise HTTPException(status_code=400, detail=f"Exact amount missing for user {uid_str}")
            user_exact_amounts[uid_str] = split.amount_owed

    method_map = {
        SplitType.EQUAL: "equal",
        SplitType.PERCENTAGE: "percentage",
        SplitType.SHARE: "shares",
        SplitType.ITEM: "exact",
    }

    try:
        from app.core.algorithms.expense_splitter import calculate_debt_distribution

        distributed = calculate_debt_distribution(
            method=method_map[expense_in.split_type],
            total_amount=expense_in.amount,
            user_ids=user_ids or None,
            user_percentages=user_percentages or None,
            user_shares=user_shares or None,
            user_exact_amounts=user_exact_amounts or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── Validate recurring flags ──────────────────────────────────────────────
    if expense_in.is_recurring and not expense_in.recurring_frequency:
        raise HTTPException(
            status_code=400,
            detail="recurring_frequency is required when is_recurring is true",
        )

    # ── Persist ───────────────────────────────────────────────────────────────
    expense = Expense(
        group_id=expense_in.group_id,
        payer_id=payer_id,
        amount=expense_in.amount,
        currency=expense_in.currency.upper(),
        description=expense_in.description,
        split_type=expense_in.split_type,
        expense_date=expense_in.expense_date,
        is_recurring=expense_in.is_recurring,
        recurring_frequency=expense_in.recurring_frequency,
        recurring_day_of_week=expense_in.recurring_day_of_week,
        recurring_day_of_month=expense_in.recurring_day_of_month,
    )
    db.add(expense)
    await db.flush()

    for uid_str, amt in distributed.items():
        original = next(
            (s for s in expense_in.splits if str(s.user_id) == uid_str), None
        )
        db.add(
            Split(
                expense_id=expense.id,
                user_id=uid_str,
                percentage=original.percentage if original else None,
                share=original.share if original else None,
                amount_owed=amt,
            )
        )

    await db.commit()
    await db.refresh(expense)
    return expense


# ── List Expenses ─────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[ExpenseResponse],
    summary="List expenses (optionally filtered by group)",
)
async def list_expenses(
    group_id: Optional[UUID] = Query(default=None, description="Filter by group"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    q = (
        select(Expense)
        .join(GroupMember, GroupMember.group_id == Expense.group_id)
        .filter(GroupMember.user_id == current_user.id)
        .options(selectinload(Expense.splits))
        .order_by(Expense.expense_date.desc())
    )
    if group_id:
        q = q.filter(Expense.group_id == group_id)

    result = await db.execute(q)
    return result.scalars().unique().all()


# ── Get Single Expense ────────────────────────────────────────────────────────

@router.get("/{expense_id}", response_model=ExpenseResponse, summary="Expense detail")
async def get_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .filter(Expense.id == expense_id)
    )
    expense = result.scalars().first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Verify membership
    membership_q = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == expense.group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not membership_q.scalars().first():
        raise HTTPException(status_code=403, detail="Access denied")

    return expense


# ── Dashboard Stats ───────────────────────────────────────────────────────────

async def _compute_stats(
    db: AsyncSession, user: User, group_id: Optional[UUID] = None
) -> DashboardStats:
    """
    Core stats computation.
    Iterates over all splits the user is involved in (as payer or ower).
    Aggregates per-group and global totals.
    """
    # Fetch all groups the user belongs to
    groups_q = await db.execute(
        select(Group)
        .join(GroupMember)
        .filter(GroupMember.user_id == user.id)
    )
    user_groups = groups_q.scalars().all()

    if group_id:
        user_groups = [g for g in user_groups if g.id == group_id]
        if not user_groups:
            raise HTTPException(status_code=403, detail="Not a member of this group")

    uid = str(user.id)
    debts_by_group: List[GroupDebt] = []
    total_to_pay = decimal.Decimal("0")
    total_owed_to_you = decimal.Decimal("0")

    for group in user_groups:
        splits_q = await db.execute(
            select(Split).join(Expense).filter(Expense.group_id == group.id)
        )
        all_splits = splits_q.scalars().all()

        you_owe = decimal.Decimal("0")
        you_are_owed = decimal.Decimal("0")

        for split in all_splits:
            payer_id = str(split.expense.payer_id)
            split_uid = str(split.user_id)
            if payer_id == split_uid:
                continue  # payer's own split
            if payer_id == uid:
                you_are_owed += split.amount_owed
            if split_uid == uid:
                you_owe += split.amount_owed

        debts_by_group.append(
            GroupDebt(
                group_id=group.id,
                group_name=group.name,
                you_owe=you_owe,
                you_are_owed=you_are_owed,
            )
        )
        total_to_pay += you_owe
        total_owed_to_you += you_are_owed

    return DashboardStats(
        total_to_pay=total_to_pay,
        total_owed_to_you=total_owed_to_you,
        net_balance=total_owed_to_you - total_to_pay,
        debts_by_group=debts_by_group,
    )


@router.get(
    "/dashboard/stats",
    response_model=DashboardStats,
    summary="Global dashboard stats for the current user",
)
async def get_global_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return await _compute_stats(db, current_user)


@router.get(
    "/dashboard/stats/group/{group_id}",
    response_model=DashboardStats,
    summary="Dashboard stats filtered to a specific group",
)
async def get_group_stats(
    group_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return await _compute_stats(db, current_user, group_id=group_id)
