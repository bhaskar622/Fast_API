from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.complaint_repository import ComplaintRepository
from app.models.user import User


class DeleteComplaintUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ComplaintRepository(session)

    async def execute(self, complaint_id: int, current_user: User) -> bool:
        complaint = await self.repo.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")

        if complaint.stage != "draft":
            raise HTTPException(status_code=400, detail="Only draft complaints can be deleted")

        if complaint.created_by != current_user.id and current_user.role == "user":
            raise HTTPException(status_code=403, detail="You can only delete your own complaints")

        await self.repo.delete(complaint)
        return True
