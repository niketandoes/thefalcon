from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
import decimal

from app.api import deps
from app.models.expense import Expense, SplitType
from app.models.split import Split
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse

router = APIRouter()

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    *,
    db: AsyncSession = Depends(deps.get_db),
    expense_in: ExpenseCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new expense with associated splits."""
    
    # Validation logic
    if expense_in.split_type == SplitType.PERCENTAGE:
        total_percentage = sum([split.percentage for split in expense_in.splits if split.percentage], decimal.Decimal(0))
        if total_percentage != decimal.Decimal("100.00"):
            raise HTTPException(status_code=400, detail="Percentages must sum up to 100")
    
    # Calculate exact owed amounts using the provided expense engine
    user_ids = []
    user_percentages = {}
    user_shares = {}
    user_exact_amounts = {}
    
    for split in expense_in.splits:
        uid_str = str(split.user_id)
        if expense_in.split_type == SplitType.EQUAL:
            user_ids.append(uid_str)
        elif expense_in.split_type == SplitType.PERCENTAGE:
            if split.percentage is None:
                raise HTTPException(status_code=400, detail="Percentage value missing")
            user_percentages[uid_str] = split.percentage
        elif expense_in.split_type == SplitType.SHARE:
            if split.share is None:
                raise HTTPException(status_code=400, detail="Share value missing")
            user_shares[uid_str] = split.share
        elif expense_in.split_type == SplitType.ITEM:
            if split.amount_owed is None:
               raise HTTPException(status_code=400, detail="Amount value missing")
            user_exact_amounts[uid_str] = split.amount_owed

    try:
        from app.core.algorithms.expense_splitter import calculate_debt_distribution
        # Note: the input SplitType enum strings match "equal", "percentage", "shares", "exact" 
        # based on SplitType lowercase equivalent or similar matching.
        # Ensure mapping aligns:
        mapped_method = {
            SplitType.EQUAL: "equal",
            SplitType.PERCENTAGE: "percentage",
            SplitType.SHARE: "shares",
            SplitType.ITEM: "exact",
        }[expense_in.split_type]

        distributed_amounts = calculate_debt_distribution(
            method=mapped_method,
            total_amount=expense_in.amount,
            user_ids=user_ids if user_ids else None,
            user_percentages=user_percentages if user_percentages else None,
            user_shares=user_shares if user_shares else None,
            user_exact_amounts=user_exact_amounts if user_exact_amounts else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    splits_to_create = []
    for uid_str, amt in distributed_amounts.items():
        original_split = next((s for s in expense_in.splits if str(s.user_id) == uid_str), None)
        splits_to_create.append(Split(
            user_id=uid_str,
            percentage=original_split.percentage if original_split else None,
            share=original_split.share if original_split else None,
            amount_owed=amt
        ))


    # Save to Database
    expense = Expense(
        group_id=expense_in.group_id,
        payer_id=current_user.id,
        amount=expense_in.amount,
        description=expense_in.description,
        split_type=expense_in.split_type
    )
    db.add(expense)
    await db.flush() # Get ID
    
    for split in splits_to_create:
        split.expense_id = expense.id
        db.add(split)
        
    await db.commit()
    await db.refresh(expense)
    
    return expense
