# app/models/task.py
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # VARCHAR with allowed values — better to use a DB ENUM or CHECK constraint in prod
    status: Mapped[str] = mapped_column(
        String(20), default="open", nullable=False
    )  # "open", "in_progress", "done"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ForeignKey("users.id") = FK constraint pointing to users table's id column
    # ondelete="SET NULL" = if the user is deleted, set owner_id to NULL
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # ForeignKey to projects
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )

    # Many Tasks → One User (the owner)
    owner: Mapped["User | None"] = relationship("User", back_populates="tasks")

    # Many Tasks → One Project
    project: Mapped["Project | None"] = relationship("Project", back_populates="tasks")
