from datetime import UTC, datetime
from uuid import UUID

from app.auth.interfaces.service import IAuthService
from app.auth.schemas import TokenPair
from app.shared.cache.interface import ICacheService
from app.shared.exceptions.types import (
    AuthenticationError,
    ConflictError,
    ValidationError,
    NotFoundError,
)
from app.shared.security.jwt import TokenManager, TokenPayload
from app.shared.security.password import PasswordManager
from app.users.interfaces.repository import IUserRepository
from app.users.models import User
from app.users.schemas import UserCreate, normalize_email


class AuthService(IAuthService):
    def __init__(
        self,
        user_repository: IUserRepository,
        cache: ICacheService,
        password_manager: PasswordManager,
        token_manager: TokenManager,
    ) -> None:
        self._users = user_repository
        self._cache = cache
        self._passwords = password_manager
        self._tokens = token_manager

    async def register(self, data: UserCreate) -> User:
        email = normalize_email(str(data.email))
        if await self._users.get_by_email(email) is not None:
            raise ConflictError("A user with this email already exists")
        return await self._users.create(
            email=email,
            first_name=data.first_name,
            last_name=data.last_name,
            hashed_password=self._passwords.hash(data.password),
        )

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self._users.get_by_email(normalize_email(email))
        if user is None or not self._passwords.verify(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        return await self._issue_token_pair(user.id)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = self._tokens.decode(refresh_token, "refresh")
        key = self._refresh_key(payload.jti)
        stored_subject = await self._cache.get(key)
        if stored_subject != str(payload.subject):
            raise AuthenticationError("Refresh token is invalid or has been revoked")

        # Delete first: a token can only be successfully rotated once.
        await self._cache.delete(key)
        if await self._users.get_by_id(payload.subject) is None:
            raise AuthenticationError("Refresh token subject no longer exists")
        return await self._issue_token_pair(payload.subject)

    async def reset_password(
        self,
        email: str,
        new_password: str,
    ) -> None:
        user = await self._users.get_by_email(normalize_email(email))

        if user is None:
            raise NotFoundError("User not found")

        if self._passwords.verify(new_password, user.hashed_password):
            raise ValidationError(
                "New password must differ from the current password"
            )

        hashed_password = self._passwords.hash(new_password)

        await self._users.update_password(
            user.id,
            hashed_password,
        )

    async def change_password(
        self, access_token: str, current_password: str, new_password: str
    ) -> None:
        payload = self._tokens.decode(access_token, "access")
        user = await self._require_user(payload.subject)
        if not self._passwords.verify(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        if self._passwords.verify(new_password, user.hashed_password):
            raise ValidationError("New password must differ from the current password")
        await self._users.update_password(user.id, self._passwords.hash(new_password))

    async def issue_password_reset_token(self, user_id: UUID) -> str:
        """Create a reset token for the future email workflow; never expose publicly."""
        await self._require_user(user_id)
        token, payload = self._tokens.create(user_id, "password_reset")
        await self._cache.set(
            self._reset_key(payload.jti),
            str(user_id),
            self._remaining_seconds(payload),
        )
        return token

    async def _issue_token_pair(self, user_id: UUID) -> TokenPair:
        access_token, access = self._tokens.create(user_id, "access")
        refresh_token, refresh = self._tokens.create(user_id, "refresh")
        refresh_seconds = self._remaining_seconds(refresh)
        await self._cache.set(
            self._refresh_key(refresh.jti), str(user_id), refresh_seconds
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in=self._remaining_seconds(access),
            refresh_expires_in=refresh_seconds,
        )

    async def _require_user(self, user_id: UUID) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise AuthenticationError("Authenticated user no longer exists")
        return user

    @staticmethod
    def _remaining_seconds(payload: TokenPayload) -> int:
        return max(1, int((payload.expires_at - datetime.now(UTC)).total_seconds()))

    @staticmethod
    def _refresh_key(jti: str) -> str:
        return f"auth:refresh:{jti}"

    @staticmethod
    def _reset_key(jti: str) -> str:
        return f"auth:password-reset:{jti}"