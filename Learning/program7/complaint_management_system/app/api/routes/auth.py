from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.usecases.commands.register_user import RegisterUserUseCase, RegisterUserCommand
from app.usecases.commands.login_user import LoginUseCase, LoginCommand
from app.schemas.user import UserResponse
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: RegisterUserCommand, db: AsyncSession = Depends(get_db)):
    return await RegisterUserUseCase(db).execute(data)


@router.post("/login")
async def login(data: LoginCommand, db: AsyncSession = Depends(get_db)):
    return await LoginUseCase(db).execute(data)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
