import redis.asyncio as aioredis
import os

class RedisClient:
    def __init__(self):
        self._client = aioredis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True,
        )
    async def get(self, key: str) -> str | None:
        return await self._client.get(key)
 
    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> None:
        await self._client.set(key, value, ex=ttl_seconds)
 
    async def delete(self, key: str) -> None:
        await self._client.delete(key)
 
    async def ping(self) -> bool:
        try:
            return await self._client.ping()
        except Exception:
            return False
