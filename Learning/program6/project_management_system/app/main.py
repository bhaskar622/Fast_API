# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.api.routes import tasks, users, projects
from app.db.base import Base
from app.db.session import engine
# import app.models  # noqa: F401 — registers all models with SQLAlchemy
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    FastAPI raises this when Pydantic validation fails (wrong types, missing fields).
    Default response is verbose — we make it cleaner.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(e) for e in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    SQLAlchemy raises this when a DB constraint is violated
    (e.g., duplicate unique email, FK violation).
    """
    logger.error(f"DB integrity error: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Data conflict — check for duplicate entries"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unexpected errors — never expose internal details to clients.
    """
    logger.exception(f"Unexpected error on {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"},
    )
