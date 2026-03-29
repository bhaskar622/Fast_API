from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base

# Stage workflow: draft → submitted → under_review → approved → resolved → closed
VALID_STAGES = {"draft", "submitted", "under_review", "approved", "resolved", "closed"}

STAGE_TRANSITIONS = {
    "draft": {"submitted"},
    "submitted": {"under_review", "draft"},       # can be sent back to draft
    "under_review": {"approved", "submitted"},     # can be sent back to submitted
    "approved": {"resolved"},
    "resolved": {"closed"},
    "closed": set(),                               # terminal state
}


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, critical

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    created_by_user: Mapped["User"] = relationship("User", foreign_keys=[created_by], back_populates="complaints")
    assigned_to_user: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to])
    detail: Mapped["ComplaintDetail | None"] = relationship("ComplaintDetail", back_populates="complaint", uselist=False)
