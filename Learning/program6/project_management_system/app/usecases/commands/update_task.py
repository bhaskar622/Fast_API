# app/usecases/commands/update_task.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.models.task import Task
from pydantic import BaseModel
from typing import Optional


class UpdateTaskCommand(BaseModel):
    """Input data for updating a task. Separate from the HTTP request schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None


class UpdateTaskUseCase:
    """
    Encapsulates ALL business logic for updating a task.

    Rules:
    - Status transitions: done → open should be forbidden
    - A user cannot have more than 50 tasks
    """

    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def execute(self, task_id: int, command: UpdateTaskCommand) -> Task:
        # Business Rule 1: Validate status can not go from 'done' to 'open'
        existing_task = await self.repo.get_by_id(task_id)
        if existing_task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        if existing_task.status == "done" and command.status == "open":
            raise HTTPException(
                status_code=400,
                detail="Cannot change status from 'done' to 'open'"
            )

        # Business Rule 2: User task limit
        if command.owner_id is not None:
            task_count = await self.repo.count_by_owner(command.owner_id)
            if task_count >= 50:
                raise HTTPException(
                    status_code=400,
                    detail="You have reached the maximum of 50 tasks"
                )

        # Create the ORM object and persist
        task = Task(
            title=command.title,
            description=command.description,
            status=command.status,
            owner_id=command.owner_id,
        )
        saved_task = await self.repo.update(task_id, task)
        return saved_task
