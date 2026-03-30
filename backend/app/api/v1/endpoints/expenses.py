"""
expenses.py — Expense tracking endpoints
  POST /expenses/                               → Log a new expense
  GET  /expenses/                               → List expenses (filterable by group_id)
  GET  /expenses/{expense_id}                   → Get expense detail
  GET  /expenses/dashboard/stats                → Aggregated global stats for current user
  GET  /expenses/dashboard/stats/group/{group_id} → Stats filtered by group
"""
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.algorithms.expense_splitter import calculate_debt_distribution, SplitMethod
from app.models.expense import Expense, SplitType
from app.models.group import Group
from app.models.group_member import GroupMember, MemberStatus
from app.models.split import Split
from app.models.user import User
from app.schemas.expense import DashboardStats, ExpenseCreate, ExpenseResponse, GroupDebt
from app.services.currency_service import convert_currency
from app.services.notification_service import notify_expense_tagged

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _require_group_membership(
    group_id: UUID, user_id: UUID, db: AsyncSession
) -> None:
    result = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.status == MemberStatus.ACCEPTED,
        )
    )
    if not result.scalars().first():
        raise HTTPException(status_code=403, detail="You are not a member of this group")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

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

    The split amounts are computed server-side using the expense_splitter
    algorithm. The `splits` list in the payload provides per-user metadata
    (user_id, percentage, share, or amount_owed depending on split_type).
    """
    # ── Validate group membership ─────────────────────────────────────────
    await _require_group_membership(expense_in.group_id, current_user.id, db)

    # Determine payer (defaults to current user)
    payer_id = expense_in.payer_id or current_user.id

    # Verify payer is in the group
    await _require_group_membership(expense_in.group_id, payer_id, db)

    # ── Compute split amounts via algorithm ───────────────────────────────
    total = Decimal(str(expense_in.amount))
    split_user_ids = [str(s.user_id) for s in expense_in.splits]

    match expense_in.split_type:
        case SplitType.EQUAL:
            computed = calculate_debt_distribution(
                SplitMethod.EQUAL, total, user_ids=split_user_ids,
            )
        case SplitType.PERCENTAGE:
            pct_map = {str(s.user_id): Decimal(str(s.percentage)) for s in expense_in.splits if s.percentage is not None}
            computed = calculate_debt_distribution(
                SplitMethod.PERCENTAGE, total, user_percentages=pct_map,
            )
        case SplitType.SHARE:
            share_map = {str(s.user_id): Decimal(str(s.share)) for s in expense_in.splits if s.share is not None}
            computed = calculate_debt_distribution(
                SplitMethod.SHARES, total, user_shares=share_map,
            )
        case SplitType.ITEM:
            exact_map = {str(s.user_id): Decimal(str(s.amount_owed)) for s in expense_in.splits if s.amount_owed is not None}
            computed = calculate_debt_distribution(
                SplitMethod.EXACT, total, user_exact_amounts=exact_map,
            )
        case _:
            raise HTTPException(status_code=400, detail=f"Unsupported split type: {expense_in.split_type}")

    # ── Persist expense ───────────────────────────────────────────────────
    expense = Expense(
        group_id=expense_in.group_id,
        payer_id=payer_id,
        amount=total,
        currency=expense_in.currency,
        description=expense_in.description,
        split_type=expense_in.split_type,
        expense_date=expense_in.expense_date,
        is_recurring=expense_in.is_recurring,
        recurring_frequency=expense_in.recurring_frequency,
        recurring_day_of_week=expense_in.recurring_day_of_week,
        recurring_day_of_month=expense_in.recurring_day_of_month,
    )
    db.add(expense)
    await db.flush()  # assign expense.id

    # ── Persist splits ────────────────────────────────────────────────────
    split_input_map = {str(s.user_id): s for s in expense_in.splits}
    for uid_str, amount_owed in computed.items():
        original = split_input_map.get(uid_str)
        split_row = Split(
            expense_id=expense.id,
            user_id=UUID(uid_str),
            amount_owed=amount_owed,
            percentage=original.percentage if original else None,
            share=original.share if original else None,
        )
        db.add(split_row)

    # ── Notify tagged users ───────────────────────────────────────────────
    payer_name = current_user.full_name or current_user.email
    for uid_str, amount_owed in computed.items():
        tagged_uid = UUID(uid_str)
        if tagged_uid != payer_id:
            await notify_expense_tagged(
                db,
                tagged_user_id=tagged_uid,
                payer_name=payer_name,
                expense_description=expense_in.description,
                amount_owed=f"{expense_in.currency} {amount_owed:.2f}",
                group_id=expense_in.group_id,
                expense_id=expense.id,
            )

    await db.commit()
    await db.refresh(expense)

    # Re-fetch with splits loaded
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .filter(Expense.id == expense.id)
    )
    return result.scalars().first()


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
    """
    Return expenses the current user is involved in (as payer or ower).
    Optionally filter to a specific group.
    """
    # Base query: expenses where user is payer OR has a split
    payer_q = select(Expense.id).filter(Expense.payer_id == current_user.id)
    split_q = select(Split.expense_id).filter(Split.user_id == current_user.id)

    if group_id is not None:
        payer_q = payer_q.filter(Expense.group_id == group_id)
        # For splits, we need to join expense to filter by group
        split_q = (
            select(Split.expense_id)
            .join(Expense, Expense.id == Split.expense_id)
            .filter(Split.user_id == current_user.id, Expense.group_id == group_id)
        )

    combined_ids = payer_q.union(split_q).subquery()

    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .filter(Expense.id.in_(select(combined_ids)))
        .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Expense detail",
)
async def get_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Return a single expense with all its splits."""
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .filter(Expense.id == expense_id)
    )
    expense = result.scalars().first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Verify access: user must be payer or in a split
    is_payer = expense.payer_id == current_user.id
    is_in_split = any(s.user_id == current_user.id for s in expense.splits)
    if not is_payer and not is_in_split:
        raise HTTPException(status_code=403, detail="Access denied")

    return expense


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------

async def _compute_stats(
    db: AsyncSession,
    user: User,
    group_id: Optional[UUID] = None,
) -> DashboardStats:
    """
    Core stats computation.
    Iterates over all splits the user is involved in (as payer or ower).
    Aggregates per-group and global totals.

    Logic:
    - For each expense where user is the payer:
        sum of OTHER users' splits = money owed TO the user
    - For each split where user owes money to a DIFFERENT payer:
        that split amount = money the user OWES
    """
    # Fetch all relevant expenses
    query = (
        select(Expense)
        .options(selectinload(Expense.splits))
        .join(Group, Group.id == Expense.group_id)
    )
    if group_id:
        query = query.filter(Expense.group_id == group_id)

    result = await db.execute(query)
    all_expenses = result.scalars().all()

    # Per-group accumulators
    group_you_owe: dict[UUID, Decimal] = {}
    group_you_are_owed: dict[UUID, Decimal] = {}
    group_names: dict[UUID, str] = {}

    for expense in all_expenses:
        gid = expense.group_id

        # Lazy-load group name
        if gid not in group_names:
            g_result = await db.execute(select(Group.name).filter(Group.id == gid))
            group_names[gid] = g_result.scalar_one()

        if expense.payer_id == user.id:
            # User paid → others' splits are owed TO user
            for s in expense.splits:
                if s.user_id != user.id:
                    group_you_are_owed[gid] = group_you_are_owed.get(gid, Decimal("0")) + s.amount_owed
        else:
            # Someone else paid → user's split is what user OWES
            for s in expense.splits:
                if s.user_id == user.id:
                    group_you_owe[gid] = group_you_owe.get(gid, Decimal("0")) + s.amount_owed

    # Build per-group response
    all_group_ids = set(group_you_owe.keys()) | set(group_you_are_owed.keys())
    debts_by_group = []
    for gid in sorted(all_group_ids, key=str):
        owe = group_you_owe.get(gid, Decimal("0"))
        owed = group_you_are_owed.get(gid, Decimal("0"))
        debts_by_group.append(
            GroupDebt(
                group_id=gid,
                group_name=group_names.get(gid, "Unknown"),
                you_owe=owe,
                you_are_owed=owed,
            )
        )

    total_to_pay = sum(group_you_owe.values(), Decimal("0"))
    total_owed_to_you = sum(group_you_are_owed.values(), Decimal("0"))

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
    """Aggregate owed/owing across all groups."""
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
    """Aggregate owed/owing for a specific group only."""
    await _require_group_membership(group_id, current_user.id, db)
    return await _compute_stats(db, current_user, group_id=group_id)