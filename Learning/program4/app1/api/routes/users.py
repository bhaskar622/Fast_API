# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from models import User
from schemas.user import UserCreateRequest, UserResponse

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
        title=data.title,
        description=data.description,
        status=data.status,
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
    if data.title is not None:
        user.title = data.title
    if data.description is not None:
        user.description = data.description
    if data.status is not None:
        user.status = data.status

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
