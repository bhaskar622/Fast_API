from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.complaint_repository import ComplaintRepository
from app.models.complaint import Complaint


class GetComplaintQuery:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int) -> Complaint:
        complaint = await self.repo.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
        return complaint
