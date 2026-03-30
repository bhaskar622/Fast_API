from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.api.routes import complaints, auth
from app.db.base import Base
from app.db.session import engine
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


app = FastAPI(title="Complaint Management System API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(complaints.router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": " → ".join(str(e) for e in error["loc"]), "message": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": "Validation failed", "errors": errors})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"DB integrity error: {exc}")
    return JSONResponse(status_code=409, content={"detail": "Data conflict — check for duplicate entries"})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error on {request.method} {request.url}")
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred"})
