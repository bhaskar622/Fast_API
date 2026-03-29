from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class ComplaintCreateRequest(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"


class ComplaintUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    assigned_to: int | None = None


class ComplaintStageUpdateRequest(BaseModel):
    stage: str


class ComplaintDetailCreateRequest(BaseModel):
    customer_name: str
    customer_email: str | None = None
    customer_phone: str | None = None
    destination: str | None = None
    complaint_type: str  # billing, service, delivery, quality, other
    provider: str | None = None
    remarks: str | None = None
    refund_amount: Decimal = Decimal("0")
    recovery_amount: Decimal = Decimal("0")
    extra_cost: Decimal = Decimal("0")


class ComplaintDetailUpdateRequest(BaseModel):
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    destination: str | None = None
    complaint_type: str | None = None
    provider: str | None = None
    remarks: str | None = None
    refund_amount: Decimal | None = None
    recovery_amount: Decimal | None = None
    extra_cost: Decimal | None = None


class ComplaintDetailResponse(BaseModel):
    id: int
    complaint_id: int
    customer_name: str
    customer_email: str | None = None
    customer_phone: str | None = None
    destination: str | None = None
    complaint_type: str
    provider: str | None = None
    remarks: str | None = None
    refund_amount: Decimal
    recovery_amount: Decimal
    extra_cost: Decimal
    financial_approved: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    stage: str
    priority: str
    created_by: int | None = None
    assigned_to: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    detail: ComplaintDetailResponse | None = None

    model_config = {"from_attributes": True}
