import asyncio
from sqlalchemy import text
from app.db.session import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT typname FROM pg_type WHERE typname IN ('memberstatus', 'notificationtype')"))
        print("Existing types:", [r[0] for r in res.fetchall()])

if __name__ == "__main__":
    asyncio.run(check())
