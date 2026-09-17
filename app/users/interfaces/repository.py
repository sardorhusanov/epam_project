from abc import ABC, abstractmethod
from uuid import UUID

from app.users.models import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str,
    ) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_password(self, user_id: UUID, hashed_password: str) -> User:
        raise NotImplementedError
