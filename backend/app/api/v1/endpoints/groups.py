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

@router.post('/', response_model=GroupResponse, status_code=status.HTTP_201_CREATED, summary='Create a new group')
async def create_group(*, db: AsyncSession=Depends(deps.get_db), group_in: GroupCreate, current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.get('/', response_model=List[GroupResponse], summary="List current user's groups")
async def read_groups(db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.get('/{group_id}', response_model=GroupDetailResponse, summary='Get group detail with members')
async def get_group_detail(group_id: UUID, db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

class AddMemberPayload(PydanticBaseModel):
    email: str

@router.post('/{group_id}/members', status_code=status.HTTP_201_CREATED, summary='Add a member to a group by email')
async def add_member(group_id: UUID, payload: AddMemberPayload, db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.delete('/{group_id}/leave', status_code=status.HTTP_200_OK, summary='Leave a group (blocked if balance is non-zero)')
async def leave_group(group_id: UUID, db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass

@router.get('/{group_id}/balances', response_model=List[DebtSummary], summary='Get simplified debt transactions for a group')
async def get_group_balances(group_id: UUID, db: AsyncSession=Depends(deps.get_db), current_user: User=Depends(deps.get_current_user)) -> Any:
    pass