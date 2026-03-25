import asyncio
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    text,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

# ============================================================
# CONFIGURATION
# ============================================================
# Change these as per your PostgreSQL local setup
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

DB_NAME = "taskdb"

# Connection to default postgres DB (used to create taskdb)
ADMIN_DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
)

# Connection to taskdb
DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{DB_NAME}"
)


# ============================================================
# BASE MODEL
# ============================================================
class Base(DeclarativeBase):
    pass


# ============================================================
# MODELS
# ============================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(datetime.timezone.utc), nullable=False)

    # Relationships
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="assignee",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignee: Mapped["User | None"] = relationship(back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


# ============================================================
# CREATE DATABASE IF NOT EXISTS
# ============================================================
async def create_database_if_not_exists():
    """
    Connect to the default 'postgres' database and create 'taskdb'
    if it doesn't already exist.
    """
    admin_engine = create_async_engine(ADMIN_DATABASE_URL, echo=True)

    try:
        async with admin_engine.connect() as conn:
            # Important: CREATE DATABASE cannot run inside a transaction
            await conn.execution_options(isolation_level="AUTOCOMMIT")

            # Check if DB exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": DB_NAME},
            )
            exists = result.scalar() is not None

            if exists:
                print(f"Database '{DB_NAME}' already exists.")
            else:
                await conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
                print(f"Database '{DB_NAME}' created successfully.")

    finally:
        await admin_engine.dispose()


# ============================================================
# CREATE TABLES
# ============================================================
async def create_tables():
    """
    Connect to taskdb and create all tables from models.
    """
    engine = create_async_engine(DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("All tables created successfully in 'taskdb'.")
    finally:
        await engine.dispose()


# ============================================================
# OPTIONAL: TEST INSERT
# ============================================================
async def seed_sample_data():
    """
    Optional sample data insert to verify async SQLAlchemy setup.
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with SessionLocal() as session:
            user = User(name="Bhaskar", email="bhaskar@example.com")
            session.add(user)
            await session.flush()  # get user.id without full commit

            project = Project(
                name="Task Management API",
                description="Async SQLAlchemy 2.0 training project",
                owner_id=user.id,
            )
            session.add(project)
            await session.flush()

            task = Task(
                title="Create async SQLAlchemy models",
                description="Create User, Project, Task models",
                status="pending",
                project_id=project.id,
                assignee_id=user.id,
            )
            session.add(task)

            await session.commit()
            print("Sample data inserted successfully.")

    finally:
        await engine.dispose()


# ============================================================
# MAIN
# ============================================================
async def main():
    await create_database_if_not_exists()
    await create_tables()

    # Uncomment if you want sample data inserted
    # await seed_sample_data()


if __name__ == "__main__":
    asyncio.run(main())