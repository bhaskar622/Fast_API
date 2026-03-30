from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.complaint_repository import ComplaintRepository
from app.models.complaint_detail import ComplaintDetail
from app.models.user import User
from app.schemas.complaint import ComplaintDetailCreateRequest, ComplaintDetailUpdateRequest

VALID_COMPLAINT_TYPES = {"billing", "service", "delivery", "quality", "other"}


class CreateComplaintDetailUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int, data: ComplaintDetailCreateRequest, current_user: User) -> ComplaintDetail:
        complaint = await self.repo.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")

        if complaint.detail is not None:
            raise HTTPException(status_code=409, detail="Complaint detail already exists")

        if data.complaint_type not in VALID_COMPLAINT_TYPES:
            raise HTTPException(status_code=400, detail=f"Complaint type must be one of: {VALID_COMPLAINT_TYPES}")

        # Only approver can set amounts > 0
        has_financials = data.refund_amount > 0 or data.recovery_amount > 0 or data.extra_cost > 0
        if has_financials and current_user.role != "approver":
            raise HTTPException(status_code=403, detail="Only approver can set financial amounts")

        detail = ComplaintDetail(
            complaint_id=complaint_id,
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            customer_phone=data.customer_phone,
            destination=data.destination,
            complaint_type=data.complaint_type,
            provider=data.provider,
            remarks=data.remarks,
            refund_amount=data.refund_amount,
            recovery_amount=data.recovery_amount,
            extra_cost=data.extra_cost,
        )
        return await self.repo.save_detail(detail)


class UpdateComplaintDetailUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int, data: ComplaintDetailUpdateRequest, current_user: User) -> ComplaintDetail:
        detail = await self.repo.get_detail_by_complaint_id(complaint_id)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Complaint detail for complaint {complaint_id} not found")

        # Check if financial fields are being modified then check if approver user is doing it
        financial_fields_changed = any([
            data.refund_amount is not None and data.refund_amount != detail.refund_amount,
            data.recovery_amount is not None and data.recovery_amount != detail.recovery_amount,
            data.extra_cost is not None and data.extra_cost != detail.extra_cost,
        ])
        if financial_fields_changed and current_user.role != "approver":
            raise HTTPException(status_code=403, detail="Only approver can modify financial amounts")

        if financial_fields_changed:
            detail.financial_approved = False

        if data.complaint_type and data.complaint_type not in VALID_COMPLAINT_TYPES:
            raise HTTPException(status_code=400, detail=f"Complaint type must be one of: {VALID_COMPLAINT_TYPES}")

        for field in ["customer_name", "customer_email", "customer_phone", "destination",
                        "complaint_type", "provider", "remarks", "refund_amount", "recovery_amount", "extra_cost"]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(detail, field, value)

        return await self.repo.save_detail(detail)


class ApproveFinancialsUseCase:
    """Only approver can approve financial details."""
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int, current_user: User) -> ComplaintDetail:
        if current_user.role != "approver":
            raise HTTPException(status_code=403, detail="Only approver can approve financials")

        detail = await self.repo.get_detail_by_complaint_id(complaint_id)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Complaint detail for complaint {complaint_id} not found")

        detail.financial_approved = True
        return await self.repo.save_detail(detail)
