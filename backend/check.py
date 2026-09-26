import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

from sqlalchemy import text
from app.db.database import engine


async def check_database():
    async with engine.connect() as connection:

        result = await connection.execute(
            text("SELECT current_database(), current_user")
        )

        print("DATABASE:", result.fetchone())

        result = await connection.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )

        print("TABLES:")

        for row in result:
            print("-", row[0])

    await engine.dispose()


asyncio.run(check_database())