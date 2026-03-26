# app/usecases/queries/get_task.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.models.task import Task


class GetTaskQuery:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def execute(self, task_id: int) -> Task:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return task


class ListTasksQuery:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def execute(self, owner_id: int | None = None) -> list[Task]:
        if owner_id is not None:
            return await self.repo.get_by_owner(owner_id)
        return await self.repo.get_all()
