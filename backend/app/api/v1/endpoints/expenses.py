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
from app.schemas.expense import DashboardStats, ExpenseCreate, ExpenseResponse, GroupDebt
from app.services.currency_service import convert_currency
router = APIRouter()

@router.post('/', response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED, summary='Log a new expense with split calculation')
async def create_expense(*, db: AsyncSession=Depends(deps.get_db), expense_in: ExpenseCreate, current_user: User=Depends(deps.get_current_user)) -> Any:
    """
    Logs an expense. Accepts all split methods (EQUAL, PERCENTAGE, SHARE, ITEM)
    and optional recurring schedule flags.
    """
    pass

@router.get('/', response_model=List[ExpenseResponse], summary='List expenses (optionally filtered by group)')
async def list_expenses(group_id: Optional[UUID]=Query(default=None, description='Filter by group'), db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.get('/{expense_id}', response_model=ExpenseResponse, summary='Expense detail')
async def get_expense(expense_id: UUID, db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

async def _compute_stats(db: AsyncSession, user: User, group_id: Optional[UUID]=None) -> DashboardStats:
    """
    Core stats computation.
    Iterates over all splits the user is involved in (as payer or ower).
    Aggregates per-group and global totals.
    """
    pass

@router.get('/dashboard/stats', response_model=DashboardStats, summary='Global dashboard stats for the current user')
async def get_global_stats(db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.get('/dashboard/stats/group/{group_id}', response_model=DashboardStats, summary='Dashboard stats filtered to a specific group')
async def get_group_stats(group_id: UUID, db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass