from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.schemas import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.shared.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.shared.security.password import (
    hash_password,
    verify_password,
)
from app.users.models import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)

    async def register(
        self,
        data: RegisterRequest,
    ) -> TokenResponse:
        existing_user = await self.repo.get_user_by_email(data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed = hash_password(data.password)

        user = await self.repo.create_user(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hashed,
        )

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
        )

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        user = await self.repo.get_user_by_email(data.email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
        )

    async def refresh(
        self,
        data: RefreshRequest,
    ) -> AccessTokenResponse:
        try:
            payload = decode_token(data.refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required",
            )

        user_id = UUID(payload["sub"])

        user = await self.repo.users.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        access = create_access_token(user.id)

        return AccessTokenResponse(
            access_token=access,
        )

    async def password_reset(
        self,
        data: PasswordResetRequest,
    ) -> dict:
        user = await self.repo.get_user_by_email(data.email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        hashed = hash_password(data.new_password)

        await self.repo.update_password(
            user=user,
            hashed_password=hashed,
        )

        return {"message": "Password reset successfully"}

    async def change_password(
        self,
        current_user: User,
        data: ChangePasswordRequest,
    ) -> dict:
        if not verify_password(
            data.current_password,
            current_user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        hashed = hash_password(data.new_password)

        await self.repo.update_password(
            user=current_user,
            hashed_password=hashed,
        )

        return {"message": "Password changed successfully"}