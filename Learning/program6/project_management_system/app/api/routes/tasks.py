# app/api/routes/tasks.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from app.usecases.commands.create_task import CreateTaskUseCase, CreateTaskCommand
from app.usecases.commands.update_task import UpdateTaskUseCase, UpdateTaskCommand
from app.usecases.commands.delete_task import DeleteTaskUseCase
from app.usecases.queries.get_task import GetTaskQuery, ListTasksQuery
from typing import Optional

from fastapi import Query
from app.schemas.pagination import PaginationParams, PaginatedResponse
import math

from app.services.auth_service import get_current_user
from app.models.user import User
from app.repositories.task_repository import TaskRepository


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Auth required
):
    command = CreateTaskCommand(
        title=data.title,
        description=data.description,
        status=data.status,
        owner_id=current_user.id,  # Always assign to logged-in user
    )
    task = await CreateTaskUseCase(db).execute(command)
    return task


@router.get("/", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    repo = TaskRepository(db)
    tasks, total = await repo.get_paginated(pagination)

    return PaginatedResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size),
    )


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    owner_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """Route is now THIN — it only translates HTTP → use case → HTTP."""
    tasks = await ListTasksQuery(db).execute(owner_id=owner_id)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await GetTaskQuery(db).execute(task_id)
    return task


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    command = CreateTaskCommand(
        title=data.title,
        description=data.description,
        status=data.status,
        owner_id=data.owner_id,
    )
    task = await CreateTaskUseCase(db).execute(command)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, data: TaskUpdateRequest, db: AsyncSession = Depends(get_db)):
    print("data ::::::::; ", data)
    command = UpdateTaskCommand(
        title=data.title or None,
        description=data.description or None,
        status=data.status or None,
        owner_id=data.owner_id or None,
    )
    task = await UpdateTaskUseCase(db).execute(task_id, command)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    await DeleteTaskUseCase(db).execute(task_id)
