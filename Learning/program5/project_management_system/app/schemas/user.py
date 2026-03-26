from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_active: bool = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
