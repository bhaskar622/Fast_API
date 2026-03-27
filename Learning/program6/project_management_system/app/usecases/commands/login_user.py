# app/usecases/commands/login_user.py
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.session_token import SessionToken
from app.services.auth_service import verify_password, generate_token
from pydantic import BaseModel


class LoginCommand(BaseModel):
    email: str
    password: str


class LoginUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, command: LoginCommand) -> dict:
        result = await self.session.execute(
            select(User).where(User.email == command.email)
        )
        user = result.scalar_one_or_none()

        # Use same error for both "user not found" and "wrong password"
        # This prevents email enumeration attacks
        if user is None or not verify_password(command.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        # Create session token valid for 24 hours
        token = SessionToken(
            user_id=user.id,
            token=generate_token(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        self.session.add(token)
        await self.session.commit()

        return {"token": token.token, "user_id": user.id, "expires_in": "24h"}
