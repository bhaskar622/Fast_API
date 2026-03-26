# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Connection string format: postgresql+asyncpg://user:password@host/dbname
# The '+asyncpg' part tells SQLAlchemy to use the async driver
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/taskdb"

# Engine = the connection pool to PostgreSQL
# echo=True prints all SQL queries to console (useful for development)
engine = create_async_engine(DATABASE_URL, echo=True)

# AsyncSessionLocal is a factory that creates new AsyncSession objects
# expire_on_commit=False prevents attributes from expiring after commit
# (important in async code — you often read data after committing)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
