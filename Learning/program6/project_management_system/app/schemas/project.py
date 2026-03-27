from pydantic import BaseModel
from datetime import datetime


class ProjectCreateRequest(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
