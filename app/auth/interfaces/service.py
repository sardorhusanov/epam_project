from abc import ABC, abstractmethod

from app.auth.schemas import TokenPair
from app.users.models import User
from app.users.schemas import UserCreate


class IAuthService(ABC):
    @abstractmethod
    async def register(self, data: UserCreate) -> User:
        raise NotImplementedError

    @abstractmethod
    async def login(self, email: str, password: str) -> TokenPair:
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, refresh_token: str) -> TokenPair:
        raise NotImplementedError

    @abstractmethod
    async def reset_password(
        self,
        email: str,
        new_password: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def change_password(
        self, access_token: str, current_password: str, new_password: str
    ) -> None:
        raise NotImplementedError