from pydantic import BaseModel
from datetime import datetime


class UserCreateRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"  # user, manager, approver


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
