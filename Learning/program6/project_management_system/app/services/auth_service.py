# app/services/auth_service.py
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.session_token import SessionToken
from app.models.user import User


def hash_password(plain_password: str) -> str:
    """
    In production use bcrypt: pip install bcrypt
    For simplicity here we use SHA256 — DO NOT use SHA256 in real apps.
    """
    import bcrypt
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed: str) -> bool:
    import bcrypt
    return bcrypt.checkpw(plain_password.encode(), hashed.encode())


def generate_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(32)  # 32 bytes → 43-char URL-safe string


async def get_current_user(
    x_auth_token: str = Header(..., description="Session token from /auth/login"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authentication dependency — inject this into any protected route.
    Reads the token from the X-Auth-Token header and returns the User.
    """
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
