# app/api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from db.session import get_db
from models import Task
from schemas.task import TaskCreateRequest, TaskResponse, TaskSearchRequest
from enum import Enum


router = APIRouter(prefix="/tasks", tags=["Tasks"])


class Status(Enum):
    open = "open"
    closed = "closed"
    in_progress = "in_progress"


@router.post("/search")
async def search_tasks(
    criteria: TaskSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    # Start with a base query
    stmt = select(Task)

    # Build dynamic filters based on provided criteria
    filters = []
    if criteria.title:
        filters.append(Task.title.contains(criteria.title))
    if criteria.description:
        filters.append(Task.description.contains(criteria.description))
    if criteria.status:
        filters.append(Task.status == criteria.status)
    if criteria.owner_id:
        filters.append(Task.owner_id == criteria.owner_id)
    if criteria.project_id:
        filters.append(Task.project_id == criteria.project_id)

    # Apply filters if any exist
    if filters:
        stmt = stmt.where(and_(*filters))

    # Execute the query
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return tasks


@router.get("/search2")
async def search_tasks2(
    title: str | None = Query(None),
    description: str | None = Query(None),
    status: Status | None = Query(None),
    owner_id: int | None = Query(None),
    project_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # Start with a base query
    stmt = select(Task)

    # Build dynamic filters based on provided criteria
    filters = []
    if title:
        filters.append(Task.title.contains(title))
    if description:
        filters.append(Task.description.contains(description))
    if status:
        filters.append(Task.status == status.value)
    if owner_id:
        filters.append(Task.owner_id == owner_id)
    if project_id:
        filters.append(Task.project_id == project_id)

    # Apply filters if any exist
    if filters:
        stmt = stmt.where(and_(*filters))

    # Execute the query
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return tasks


@router.get("/search3")
async def search_tasks3(
    search: TaskSearchRequest = Depends(),  # Automatically parse query params into Pydantic model
    db: AsyncSession = Depends(get_db),
):
    # Start with a base query
    stmt = select(Task)

    # Build dynamic filters based on provided criteria
    filters = []
    if search.title:
        filters.append(Task.title.contains(search.title))
    if search.description:
        filters.append(Task.description.contains(search.description))
    if search.status:
        filters.append(Task.status == search.status)
    if search.owner_id:
        filters.append(Task.owner_id == search.owner_id)
    if search.project_id:
        filters.append(Task.project_id == search.project_id)

    # Apply filters if any exist
    if filters:
        stmt = stmt.where(and_(*filters))

    # Execute the query
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return tasks


@router.get("/task_by_status")  # response_model=TaskResponse
async def get_task_by_status(status: Status, db: AsyncSession = Depends(get_db)):
    """
    .where() filters the query: adds WHERE id = :task_id
    session.get() is a shortcut for fetching by primary key
    """
    result = await db.execute(
        select(Task).where(Task.status == status.value)
    )
    # tasks = result.scalars().first()
    # tasks = result.scalars().all()  # it gives list of object like [<OBJECT>]
    tasks = result.scalars().one()
    print("Task detail ::::::::::::::::::: ", tasks)
    return tasks


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
db: AsyncSession = Depends(get_db)  # Injects a fresh DB session
):
    """
    select(Task) builds: SELECT id, title, description, ... FROM tasks
    session.execute() runs the query asynchronously
    result.scalars() extracts the ORM objects (not raw rows)
    .all() collects into a list
    """
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """
    .where() filters the query: adds WHERE id = :task_id
    session.get() is a shortcut for fetching by primary key
    """
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

# Filter by status
# async def get_tasks_by_status(db: AsyncSession, status: str) -> list[Task]:
#     result = await db.execute(
#         select(Task).where(Task.status == status)
#     )
#     return result.scalars().all()





@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Create the ORM object
    Step 2: session.add() — stages it for insert (does NOT hit DB yet)
    Step 3: session.commit() — writes to DB, assigns the auto-generated ID
Step 4: session.refresh() — reloads the object from DB (to get server-set values like created_at)
    """
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)  # Loads server_default values (e.g. created_at)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, data: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Only update provided fields
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status

    # SQLAlchemy detects attribute changes automatically — no need to session.add() again
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    await db.delete(task)
    await db.commit()
