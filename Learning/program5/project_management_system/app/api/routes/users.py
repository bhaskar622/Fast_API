# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
db: AsyncSession = Depends(get_db)  # Injects a fresh DB session
):
    """
    select(User) builds: SELECT id, title, description, ... FROM users
    session.execute() runs the query asynchronously
    result.scalars() extracts the ORM objects (not raw rows)
    .all() collects into a list
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    .where() filters the query: adds WHERE id = :user_id
    session.get() is a shortcut for fetching by primary key
    """
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Create the ORM object
    Step 2: session.add() — stages it for insert (does NOT hit DB yet)
    Step 3: session.commit() — writes to DB, assigns the auto-generated ID
Step 4: session.refresh() — reloads the object from DB (to get server-set values like created_at)
    """
    user = User(
        name=data.name,
        email=data.email,
        password_hash=data.password,  # In real app, hash this!
        is_active=data.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)  # Loads server_default values (e.g. created_at)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Only update provided fields
    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.password = data.password
    if data.is_active is not None:
        user.is_active = data.is_active

    # SQLAlchemy detects attribute changes automatically — no need to session.add() again
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    await db.delete(user)
    await db.commit()
