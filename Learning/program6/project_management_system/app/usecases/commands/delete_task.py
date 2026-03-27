# app/usecases/commands/delete_task.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository


class DeleteTaskUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def execute(self, task_id: int) -> bool:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        if task.status == 'in_progress':
            raise HTTPException(status_code=404, detail=f"Task {task_id} can not be deleted, Task is in 'in_progress'")
        await self.repo.delete(task)
        return True
