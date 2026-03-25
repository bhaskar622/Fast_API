"""
1. Set up a local PostgreSQL database called `taskdb`
2. Create all three models: `User`, `Project`, `Task`
3. Run `scripts/create_tables.py` to create the tables
4. Run `scripts/seed_data.py` to insert test data
5. Connect with a DB client (DBeaver/pgAdmin) and verify the tables and data exist
6. Write a simple script that reads all tasks using a raw async session
"""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)

app = FastAPI(title="SQL Alchemy Table Create", version="1.0.0")


POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

DB_NAME = "taskdb"

ADMIN_DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}/postgres"
)

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}/{DB_NAME}"
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="pending", nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


@app.get("/")
def health_check():
    """
    The simplest possible endpoint.
    Returns a JSON response: {"status": "ok"}
    """
    return {"status": "ok"}


async def create_tables():
    """
    Connect to taskdb and create all tables from models.
    """
    admin_engine = create_async_engine(ADMIN_DATABASE_URL, echo=True)
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with admin_engine.connect() as admin_conn:
        await admin_conn.execution_options(isolation_level="AUTOCOMMIT")
        await admin_conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
        print(f"Database '{DB_NAME}' created successfully.")
    await admin_engine.dispose()
    async with engine.begin() as conn:
        print("Engine connection object : ", conn)
        await conn.run_sync(Base.metadata.create_all)

    print("All tables created successfully in 'taskdb'.")


@app.get("/create_all")
async def create_all_models():
    await create_tables()
    return {"status": "Success", "message": "All tables created successfully in 'taskdb'."}


async def seed_sample_data():
    """
    Optional sample data insert to verify async SQLAlchemy setup.
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    # SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # user = User(name="Bhaskar", email="bhaskar@example.com")
        # session.add(user)
        # await session.flush()  # get user.id without full commit
        new_user = User(name="Bhavik", email="bhavik@mail.local")
        session.add(new_user)
        await session.commit()

        # project = Project(
        #     name="Task Management API",
        #     description="Async SQLAlchemy 2.0 training project",
        #     user_id=new_user.id,
        # )
        # session.add(project)
        # await session.flush()
        new_project = Project(
            name="FastAPI Learning",
            description="Learning FastAPI with SQLALchemy",
            user_id=new_user.id
        )
        session.add(new_project)
        await session.commit()

        # task = Task(
        #     title="Create async SQLAlchemy models",
        #     description="Create User, Project, Task models",
        #     status="pending",
        #     project_id=project.id,
        #     assignee_id=user.id,
        # )
        # session.add(task)
        # await session.commit()
        new_task = Task(
            title="Learn FastAPI",
            description="Learn FastAPI with SQLALchemy",
            status="completed",
            project_id=new_project.id,
            assignee_id=new_user.id
        )
        session.add(new_task)
        await session.commit()

        print("Sample data inserted successfully.")


@app.get("/seed_data")
async def seed_data_in_models():
    await seed_sample_data()
    return {"status": "Success", "message": "All tables created successfully in 'taskdb'."}
