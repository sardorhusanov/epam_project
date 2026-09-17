from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

import jwt

from app.shared.config.settings import Settings
from app.shared.exceptions.types import AuthenticationError

TokenType = Literal["access", "refresh", "password_reset"]


@dataclass(frozen=True, slots=True)
class TokenPayload:
    subject: UUID
    token_type: TokenType
    jti: str
    issued_at: datetime
    expires_at: datetime


class TokenManager:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.JWT_SECRET_KEY
        self._algorithm = settings.JWT_ALGORITHM
        self._lifetimes = {
            "access": timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "refresh": timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            "password_reset": timedelta(
                minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            ),
        }

    def create(self, subject: UUID, token_type: TokenType) -> tuple[str, TokenPayload]:
        now = datetime.now(UTC)
        payload = TokenPayload(
            subject=subject,
            token_type=token_type,
            jti=str(uuid4()),
            issued_at=now,
            expires_at=now + self._lifetimes[token_type],
        )
        encoded = jwt.encode(
            {
                "sub": str(payload.subject),
                "type": payload.token_type,
                "jti": payload.jti,
                "iat": payload.issued_at,
                "exp": payload.expires_at,
            },
            self._secret,
            algorithm=self._algorithm,
        )
        return encoded, payload

    def decode(self, token: str, expected_type: TokenType) -> TokenPayload:
        try:
            data = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            if data.get("type") != expected_type:
                raise AuthenticationError("Invalid token type")
            subject = UUID(data["sub"])
            jti = str(data["jti"])
            issued_at = datetime.fromtimestamp(int(data["iat"]), tz=UTC)
            expires_at = datetime.fromtimestamp(int(data["exp"]), tz=UTC)
        except AuthenticationError:
            raise
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid or expired token") from exc
        return TokenPayload(
            subject=subject,
            token_type=expected_type,
            jti=jti,
            issued_at=issued_at,
            expires_at=expires_at,
        )
