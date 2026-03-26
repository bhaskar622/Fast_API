# app/models/user.py
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class User(Base):
    # __tablename__ is REQUIRED — it sets the actual PostgreSQL table name
    __tablename__ = "users"

    # Mapped[int] = type hint. mapped_column() = column definition
    # primary_key=True → this is the PK, auto-incremented by PostgreSQL
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # String(255) = VARCHAR(255) in SQL
    # unique=True = UNIQUE constraint
    # index=True = creates a DB index for faster lookups
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # nullable=False = NOT NULL constraint
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # The actual bcrypt hash is stored here, never the plain password
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Boolean field — defaults to True (active user)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # server_default=func.now() means PostgreSQL sets this, not Python
    # This is more reliable than Python datetime.now() in distributed systems
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship — tells SQLAlchemy that a User HAS MANY Tasks
    # back_populates="owner" means Task model has an 'owner' attribute pointing back
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
