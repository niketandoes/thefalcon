from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, groups, expenses, notifications

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
