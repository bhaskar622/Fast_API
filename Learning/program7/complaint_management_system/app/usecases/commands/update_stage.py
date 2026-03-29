from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.complaint_repository import ComplaintRepository
from app.models.complaint import Complaint, STAGE_TRANSITIONS
from app.models.user import User

# Which roles can perform which stage transitions
STAGE_ROLE_PERMISSIONS = {
    ("draft", "submitted"): {"user", "manager", "approver"},
    ("submitted", "draft"): {"manager", "approver"},
    ("submitted", "under_review"): {"manager", "approver"},
    ("under_review", "approved"): {"approver"},
    ("under_review", "submitted"): {"manager", "approver"},
    ("approved", "resolved"): {"manager", "approver"},
    ("resolved", "closed"): {"manager", "approver"},
}


class UpdateStageUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int, new_stage: str, current_user: User) -> Complaint:
        complaint = await self.repo.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")

        current_stage = complaint.stage

        # Validate transition is allowed
        allowed_next = STAGE_TRANSITIONS.get(current_stage, set())
        if new_stage not in allowed_next:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{current_stage}' to '{new_stage}'. Allowed: {allowed_next}"
            )

        # Validate role permission for this transition
        allowed_roles = STAGE_ROLE_PERMISSIONS.get((current_stage, new_stage), set())
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.role}' cannot perform transition '{current_stage}' → '{new_stage}'"
            )

        # Require complaint detail before submitting
        if new_stage == "submitted" and complaint.detail is None:
            raise HTTPException(
                status_code=400,
                detail="Complaint detail (customer, type) is required before submitting"
            )

        # Require financial approval before resolving
        if new_stage == "resolved" and complaint.detail:
            has_financials = (
                complaint.detail.refund_amount > 0
                or complaint.detail.recovery_amount > 0
                or complaint.detail.extra_cost > 0
            )
            if has_financials and not complaint.detail.financial_approved:
                raise HTTPException(
                    status_code=400,
                    detail="Financial details must be approved before resolving"
                )

        complaint.stage = new_stage
        return await self.repo.save(complaint)
