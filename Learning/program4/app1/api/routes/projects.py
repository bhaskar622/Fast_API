# app/api/routes/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from models import Project
from schemas.project import ProjectCreateRequest, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
db: AsyncSession = Depends(get_db)  # Injects a fresh DB session
):
    """
    select(Project) builds: SELECT id, title, description, ... FROM projects
    session.execute() runs the query asynchronously
    result.scalars() extracts the ORM objects (not raw rows)
    .all() collects into a list
    """
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    .where() filters the query: adds WHERE id = :project_id
    session.get() is a shortcut for fetching by primary key
    """
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Create the ORM object
    Step 2: session.add() — stages it for insert (does NOT hit DB yet)
    Step 3: session.commit() — writes to DB, assigns the auto-generated ID
Step 4: session.refresh() — reloads the object from DB (to get server-set values like created_at)
    """
    project = Project(
        title=data.title,
        description=data.description,
        status=data.status,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)  # Loads server_default values (e.g. created_at)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, data: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Only update provided fields
    if data.title is not None:
        project.title = data.title
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = data.status

    # SQLAlchemy detects attribute changes automatically — no need to session.add() again
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    await db.delete(project)
    await db.commit()
