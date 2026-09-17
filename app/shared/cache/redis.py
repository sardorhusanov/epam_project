from redis.asyncio import Redis

from app.shared.cache.interface import ICacheService


class RedisCacheService(ICacheService):
    def __init__(self, redis_url: str) -> None:
        self._client: Redis = Redis.from_url(redis_url, decode_responses=True)

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._client.set(key, value, ex=ttl_seconds)

    async def get(self, key: str) -> str | None:
        value = await self._client.get(key)
        return str(value) if value is not None else None

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def close(self) -> None:
        await self._client.aclose()
