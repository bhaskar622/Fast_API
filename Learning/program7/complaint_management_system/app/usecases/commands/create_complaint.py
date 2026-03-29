from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.complaint_repository import ComplaintRepository
from app.models.complaint import Complaint, VALID_STAGES
from app.models.user import User
from pydantic import BaseModel


VALID_PRIORITIES = {"low", "medium", "high", "critical"}


class CreateComplaintCommand(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"


class CreateComplaintUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, command: CreateComplaintCommand, current_user: User) -> Complaint:
        if not command.title or not command.title.strip():
            raise HTTPException(status_code=400, detail="Title is required")

        if command.priority not in VALID_PRIORITIES:
            raise HTTPException(status_code=400, detail=f"Priority must be one of: {VALID_PRIORITIES}")

        complaint = Complaint(
            title=command.title,
            description=command.description,
            stage="draft",
            priority=command.priority,
            created_by=current_user.id,
        )
        return await self.repo.save(complaint)
