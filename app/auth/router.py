from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.interfaces.service import IAuthService
from app.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    PasswordResetRequest,
    RefreshRequest,
    TokenPair,
)
from app.container import Container
from app.users.schemas import UserCreate, UserResponse

router = APIRouter(tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def require_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer access token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def register(
    data: UserCreate,
    service: Annotated[IAuthService, Depends(Provide[Container.auth_service])],
) -> UserResponse:
    user = await service.register(data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPair)
@inject
async def login(
    data: LoginRequest,
    service: Annotated[IAuthService, Depends(Provide[Container.auth_service])],
) -> TokenPair:
    return await service.login(str(data.email), data.password)


@router.post("/refresh", response_model=TokenPair)
@inject
async def refresh(
    data: RefreshRequest,
    service: Annotated[IAuthService, Depends(Provide[Container.auth_service])],
) -> TokenPair:
    return await service.refresh(data.refresh_token)


@router.post("/password_reset", response_model=MessageResponse)
@inject
async def password_reset(
    data: PasswordResetRequest,
    service: Annotated[IAuthService, Depends(Provide[Container.auth_service])],
) -> MessageResponse:
    await service.reset_password(data.reset_token, data.new_password)
    return MessageResponse(message="Password reset successfully")


@router.post("/change_password", response_model=MessageResponse)
@inject
async def change_password(
    data: ChangePasswordRequest,
    access_token: Annotated[str, Depends(require_bearer_token)],
    service: Annotated[IAuthService, Depends(Provide[Container.auth_service])],
) -> MessageResponse:
    await service.change_password(
        access_token, data.current_password, data.new_password
    )
    return MessageResponse(message="Password changed successfully")
