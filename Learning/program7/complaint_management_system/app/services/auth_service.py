import secrets
from datetime import datetime, timezone
from fastapi import HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.session_token import SessionToken
from app.models.user import User


def hash_password(plain_password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed: str) -> bool:
    import bcrypt
    return bcrypt.checkpw(plain_password.encode(), hashed.encode())


def generate_token() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(
    x_auth_token: str = Header(..., description="Session token from /auth/login"),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(
        select(SessionToken)
        .where(SessionToken.token == x_auth_token)
        .where(SessionToken.expires_at > datetime.now(timezone.utc))
    )
    token_obj = result.scalar_one_or_none()
    if token_obj is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await db.get(User, token_obj.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_role(*allowed_roles: str):
    """Dependency factory: returns a dependency that checks the user's role."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.role}' not allowed. Required: {allowed_roles}"
            )
        return current_user
    return role_checker
