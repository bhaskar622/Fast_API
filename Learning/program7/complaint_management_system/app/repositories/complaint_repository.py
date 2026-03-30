from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.complaint import Complaint
from app.models.complaint_detail import ComplaintDetail
from app.schemas.pagination import PaginationParams
from typing import Optional


class ComplaintRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, complaint_id: int) -> Optional[Complaint]:
        result = await self.session.execute(
            select(Complaint)
            .options(selectinload(Complaint.detail))
            .where(Complaint.id == complaint_id)
        )
        return result.scalar_one_or_none()

    # took help from ai the data was written but the process was not getting completed
    async def save(self, complaint: Complaint) -> Complaint:
        self.session.add(complaint)
        await self.session.commit()
        # Re-fetch with eager load to avoid MissingGreenlet on relationship access
        return await self.get_by_id(complaint.id)

    async def delete(self, complaint: Complaint) -> None:
        await self.session.delete(complaint)
        await self.session.commit()

    async def get_paginated(self, pagination: PaginationParams) -> tuple[list[Complaint], int]:
        count_result = await self.session.execute(select(func.count(Complaint.id)))
        total = count_result.scalar() or 0

        result = await self.session.execute(
            select(Complaint)
            .options(selectinload(Complaint.detail))
            .order_by(Complaint.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        complaints = result.scalars().all()
        return complaints, total

    async def save_detail(self, detail: ComplaintDetail) -> ComplaintDetail:
        self.session.add(detail)
        await self.session.commit()
        await self.session.refresh(detail)
        return detail

    async def get_detail_by_complaint_id(self, complaint_id: int) -> Optional[ComplaintDetail]:
        result = await self.session.execute(
            select(ComplaintDetail).where(ComplaintDetail.complaint_id == complaint_id)
        )
        return result.scalar_one_or_none()
