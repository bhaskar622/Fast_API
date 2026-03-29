# app/db/session.py (updated)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    This is a FastAPI dependency that:
    1. Opens a new database session
    2. Yields it to the route handler
    3. Closes it automatically after the response is sent

    'async with' ensures the session is ALWAYS closed, even if an exception occurs.
    'yield' is what makes this a FastAPI dependency generator — the code AFTER yield
    runs as cleanup, after the route handler completes.
    """
    async with AsyncSessionLocal() as session:
        yield session
        # Session is automatically closed here, even on errors
