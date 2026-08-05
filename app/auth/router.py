from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import AuthService
from app.shared.db.database import get_db
from app.shared.security.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.login(data)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.refresh(data)


@router.post(
    "/password_reset",
)
async def password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.password_reset(data)


@router.post(
    "/change_password",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.change_password(current_user, data)