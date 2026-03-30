from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.complaint_repository import ComplaintRepository
from app.models.complaint import Complaint
from app.models.user import User
from app.usecases.commands.create_complaint import VALID_PRIORITIES
from pydantic import BaseModel


class UpdateComplaintCommand(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    assigned_to: int | None = None


class UpdateComplaintUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int, command: UpdateComplaintCommand, current_user: User) -> Complaint:
        complaint = await self.repo.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")

        if complaint.created_by != current_user.id and current_user.role == "user":
            raise HTTPException(status_code=403, detail="You can only update your own complaints")

        if complaint.stage == "closed":
            raise HTTPException(status_code=400, detail="Cannot update a closed complaint")

        if command.priority and command.priority not in VALID_PRIORITIES:
            raise HTTPException(status_code=400, detail=f"Priority must be one of: {VALID_PRIORITIES}")

        if command.title is not None:
            complaint.title = command.title
        if command.description is not None:
            complaint.description = command.description
        if command.priority is not None:
            complaint.priority = command.priority
        if command.assigned_to is not None:
            if current_user.role not in ("manager", "approver"):
                raise HTTPException(status_code=403, detail="Only manager/approver can assign complaints")
            complaint.assigned_to = command.assigned_to

        return await self.repo.save(complaint)
