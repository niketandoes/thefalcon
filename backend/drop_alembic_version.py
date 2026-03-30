import asyncio
from sqlalchemy import text
from app.db.session import engine

async def drop():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        print("Dropped alembic_version table successfully.")

if __name__ == "__main__":
    asyncio.run(drop())
