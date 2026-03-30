import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
import app.models  # Ensures all models are registered

async def apply_schema():
    print("Initializing database...")
    async with engine.begin() as conn:
        print("Creating database extensions (citext, pgcrypto)...")
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "citext";'))
        
        print("Creating database tables using SQLAlchemy if they don't exist...")
        # This safely creates any missing tables and will NOT drop existing ones.
        await conn.run_sync(Base.metadata.create_all)
        
    print("Tables verified/created successfully.")

if __name__ == "__main__":
    asyncio.run(apply_schema())
