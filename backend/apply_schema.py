import asyncio
from app.db.session import engine
from app.db.base import Base
import app.models  # Ensures all models are registered

async def apply_schema():
    print("Creating database tables using SQLAlchemy if they don't exist...")
    async with engine.begin() as conn:
        # This safely creates any missing tables and will NOT drop existing ones.
        await conn.run_sync(Base.metadata.create_all)
    print("Tables verified/created successfully.")

if __name__ == "__main__":
    asyncio.run(apply_schema())
