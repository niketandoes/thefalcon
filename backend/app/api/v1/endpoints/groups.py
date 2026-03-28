from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, List

from app.api import deps
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate, GroupResponse

router = APIRouter()

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    group_in: GroupCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # 1. Create the group
    group = Group(name=group_in.name, description=group_in.description)
    db.add(group)
    await db.flush() # Get the ID
    
    # 2. Add current user as a member
    member = GroupMember(user_id=current_user.id, group_id=group.id)
    db.add(member)
    
    await db.commit()
    await db.refresh(group)
    return group

@router.get("/", response_model=List[GroupResponse])
async def read_groups(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Fetch groups where user is a member
    query = select(Group).join(GroupMember).filter(GroupMember.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()

from app.schemas.expense import DebtSummary
from app.models.expense import Expense
from app.models.split import Split
from app.core.algorithms.debt_simplifier import simplify_debts
from decimal import Decimal

@router.get("/{id}/balances", response_model=List[DebtSummary])
async def get_group_balances(
    id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # 1. Fetch all expenses for the group and deeply join splits
    query = select(Expense).filter(Expense.group_id == id)
    result = await db.execute(query)
    expenses = result.scalars().unique().all() # Unique handles the one-to-many relationship correctly if eager loaded
    
    # Needs to load splits correctly for balances. E.g async joins. 
    # For now, simplistic approach since we didn't setup eager loading on the root query:
    query_splits = select(Split).join(Expense).filter(Expense.group_id == id)
    result_splits = await db.execute(query_splits)
    all_splits = result_splits.scalars().all()

    # Dictionary user_id -> balance
    balances: dict[str, Decimal] = {}

    for split in all_splits:
        # Increase 'payer' balance
        payer_id = str(split.expense.payer_id)
        if payer_id not in balances: balances[payer_id] = Decimal("0")
        
        # Owed amount is deducted from the split user
        owed_uid = str(split.user_id)
        if owed_uid not in balances: balances[owed_uid] = Decimal("0")
        
        # Payer paid the total, but split only tells us their share is owed to payer.
        # Wait, the payer gets +amount_owed, user gets -amount_owed.
        if payer_id != owed_uid:
            balances[payer_id] += split.amount_owed
            balances[owed_uid] -= split.amount_owed

    # Simplify
    return simplify_debts(balances)

