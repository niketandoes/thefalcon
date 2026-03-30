import asyncio
import os
from sqlalchemy import text
from app.db.session import engine

async def apply_schema():
    print("Applying schema from schema.sql...")
    with open("schema.sql", "r") as f:
        sql = f.read()
    
    async with engine.begin() as conn:
        # Split by semicolon to execute one-by-one (sa.text can have issues with multiple statements in some drivers)
        # But for PostgreSQL, multi-statement strings usually work with engine.execute
        # However, to be extra safe with asyncpg, we can use the raw connection or execute in blocks.
        # Actually, asyncpg doesn't support multiple commands in one execute() unless using raw connection.
        # We'll use a simple loop over blocks separated by -- §
        blocks = sql.split("-- §")
        for block in blocks:
            if not block.strip(): continue
            cmds = block.split(";")
            for cmd in cmds:
                if not cmd.strip(): continue
                await conn.execute(text(cmd.strip()))
    
    print("Schema applied successfully.")

if __name__ == "__main__":
    asyncio.run(apply_schema())
