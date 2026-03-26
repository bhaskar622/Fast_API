# scripts/create_tables.py
import asyncio
from app.db.session import engine
from app.db.base import Base

# Import models so Base knows about them
from app.models.user import User
from app.models.project import Project
from app.models.task import Task


async def create_all():
    """Drops all tables and recreates them. Use ONLY in development."""
    async with engine.begin() as conn:
        # Drop everything first (clean slate)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables defined in our models
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")
asyncio.run(create_all())
