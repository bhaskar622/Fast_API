# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import tasks, users, projects
from db.base import Base
from db.session import engine
import models  # noqa: F401 — registers all models with SQLAlchemy


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Task Manager API", lifespan=lifespan)

# Register route groups with prefixes
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
