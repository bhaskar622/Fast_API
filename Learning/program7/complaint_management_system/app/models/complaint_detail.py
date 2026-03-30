from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal
from app.db.base import Base


class ComplaintDetail(Base):
    __tablename__ = "complaint_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id", ondelete="CASCADE"), unique=True, nullable=False)

    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(200), nullable=True)
    complaint_type: Mapped[str] = mapped_column(String(50), nullable=False)  # billing, service, delivery, quality, other
    provider: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Financial fields
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    recovery_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    extra_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    financial_approved: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="detail")
