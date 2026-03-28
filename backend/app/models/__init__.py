# Import all models here so that Alembic can detect them
from app.db.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.group import Group  # noqa: F401
from app.models.group_member import GroupMember  # noqa: F401
from app.models.expense import Expense, SplitType, RecurringFrequency  # noqa: F401
from app.models.split import Split  # noqa: F401
