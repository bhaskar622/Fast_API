# app/usecases/commands/create_task.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.models.task import Task
from pydantic import BaseModel
from typing import Optional


class CreateTaskCommand(BaseModel):
    """Input data for creating a task. Separate from the HTTP request schema."""
    title: str
    description: Optional[str] = None
    status: str = "open"
    owner_id: Optional[int] = None


class CreateTaskUseCase:
    """
    Encapsulates ALL business logic for creating a task.

    Rules:
    - Title cannot be empty
    - Status must be 'open' or 'in_progress' for new tasks
    - A user cannot have more than 50 tasks
    """

    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def execute(self, command: CreateTaskCommand) -> Task:
        # Business Rule 1: Validate status for new tasks
        allowed_initial_statuses = {"open", "in_progress"}
        if command.status not in allowed_initial_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"New tasks must have status: {allowed_initial_statuses}"
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
        saved_task = await self.repo.save(task)
        return saved_task
