# app/repositories/task_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from typing import Optional


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        return await self.session.get(Task, task_id)

    async def get_all(self) -> list[Task]:
        result = await self.session.execute(select(Task))
        return result.scalars().all()

    async def get_by_owner(self, owner_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task).where(Task.owner_id == owner_id)
        )
        return result.scalars().all()

    async def count_by_owner(self, owner_id: int) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(Task.id)).where(Task.owner_id == owner_id)
        )
        return result.scalar() or 0

    async def save(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(self, task_id: int, data: Task) -> Task:
        task = await self.session.get(Task, task_id)
        # Only update provided fields
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status
        if data.owner_id is not None:
            task.owner_id = data.owner_id
        # SQLAlchemy detects attribute changes automatically — no need to session.add() again
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()
