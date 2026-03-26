from pydantic import BaseModel
from datetime import datetime


class TaskCreateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str = "open"
    owner_id: int | None = None
    project_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    created_at: datetime | None = None
    owner_id: int | None = None
    project_id: int | None = None

    model_config = {"from_attributes": True}


class TaskSearchRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str = "open"
    owner_id: int | None = None
    project_id: int | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    owner_id: int | None = None
    # project_id: int | None = None
