import hashlib
from app.db.redis_client import RedisClient
 
 
DEFAULT_TTL_SECONDS = 86400  # 24 hours
 
 
class ExactCache:
 
    def __init__(self):
        self.redis = RedisClient()
 
    async def lookup(self, query: str) -> str | None:
        """Returns cache_id if exact match exists, else None."""
        key = self._hash(query)
        return await self.redis.get(key)
 
    async def store(self, query: str, cache_id: str, ttl: int = DEFAULT_TTL_SECONDS) -> None:
        """Store query → cache_id after L3 generation."""
        key = self._hash(query)
        await self.redis.set(key, cache_id, ttl_seconds=ttl)
 
    async def invalidate(self, query: str) -> None:
        key = self._hash(query)
        await self.redis.delete(key)
 
    async def is_available(self) -> bool:
        return await self.redis.ping()
 
    def _hash(self, query: str) -> str:
        normalized = query.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()