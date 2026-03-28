from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal
from app.models.expense import SplitType, RecurringFrequency


# ── Split schemas ─────────────────────────────────────────────────────────────

class SplitBase(BaseModel):
    user_id: UUID
    percentage: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    share: Optional[int] = Field(default=None, ge=1)
    amount_owed: Optional[condecimal(max_digits=10, decimal_places=2)] = None


class SplitCreate(SplitBase):
    pass


class SplitResponse(SplitBase):
    id: UUID
    expense_id: UUID
    amount_owed: condecimal(max_digits=10, decimal_places=2)

    class Config:
        from_attributes = True


# ── Expense schemas ───────────────────────────────────────────────────────────

class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    split_type: SplitType
    group_id: UUID
    expense_date: date = Field(default_factory=date.today)


class ExpenseCreate(ExpenseBase):
    # payer_id is optional in payload – defaults to the authenticated user
    payer_id: Optional[UUID] = None
    splits: List[SplitCreate]
    # Recurring fields
    is_recurring: bool = False
    recurring_frequency: Optional[RecurringFrequency] = None
    recurring_day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    recurring_day_of_month: Optional[int] = Field(default=None, ge=1, le=31)


class ExpenseResponse(ExpenseBase):
    id: UUID
    payer_id: UUID
    is_recurring: bool
    recurring_frequency: Optional[RecurringFrequency] = None
    recurring_day_of_week: Optional[int] = None
    recurring_day_of_month: Optional[int] = None
    created_at: datetime
    splits: List[SplitResponse] = []

    class Config:
        from_attributes = True


# ── Debt / balance schemas ────────────────────────────────────────────────────

class DebtSummary(BaseModel):
    """A single simplified payment: from_user_id owes to_user_id the given amount."""
    from_user_id: UUID
    to_user_id: UUID
    amount: condecimal(max_digits=10, decimal_places=2)


class GroupDebt(BaseModel):
    """Per-group debt summary returned by the dashboard stats endpoint."""
    group_id: UUID
    group_name: str
    you_owe: Decimal
    you_are_owed: Decimal


class DashboardStats(BaseModel):
    """Aggregated dashboard statistics for the current user."""
    total_to_pay: Decimal
    total_owed_to_you: Decimal
    net_balance: Decimal
    debts_by_group: List[GroupDebt]
