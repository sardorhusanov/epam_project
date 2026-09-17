from abc import ABC, abstractmethod


class ICacheService(ABC):
    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
