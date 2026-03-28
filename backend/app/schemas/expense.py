from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, condecimal
from app.models.expense import SplitType

class SplitBase(BaseModel):
    user_id: UUID
    # Optional fields based on split type
    percentage: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    share: Optional[int] = None
    amount_owed: Optional[condecimal(max_digits=10, decimal_places=2)] = None

class SplitCreate(SplitBase):
    pass

class SplitResponse(SplitBase):
    id: UUID
    expense_id: UUID
    amount_owed: condecimal(max_digits=10, decimal_places=2)

    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    description: str
    amount: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0)
    split_type: SplitType
    group_id: UUID

class ExpenseCreate(ExpenseBase):
    splits: List[SplitCreate]

class ExpenseResponse(ExpenseBase):
    id: UUID
    payer_id: UUID
    created_at: datetime
    splits: List[SplitResponse] = []

    class Config:
        from_attributes = True

# Helper schema for Debt Simplification
class DebtSummary(BaseModel):
    from_user_id: UUID
    to_user_id: UUID
    amount: condecimal(max_digits=10, decimal_places=2)
