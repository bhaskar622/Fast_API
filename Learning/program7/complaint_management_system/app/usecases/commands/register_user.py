from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.services.auth_service import hash_password
from pydantic import BaseModel


class RegisterUserCommand(BaseModel):
    email: str
    name: str
    password: str
    role: str = "user"


VALID_ROLES = {"user", "manager", "approver"}


class RegisterUserUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, command: RegisterUserCommand) -> User:
        if command.role not in VALID_ROLES:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {VALID_ROLES}")

        existing = await self.session.execute(
            select(User).where(User.email == command.email)
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=409, detail="Email already registered")

        if len(command.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

        user = User(
            email=command.email,
            name=command.name,
            password_hash=hash_password(command.password),
            role=command.role,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
