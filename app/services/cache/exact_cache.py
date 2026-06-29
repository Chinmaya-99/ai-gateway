class ExactCache:
    """
    L1 exact cache — SHA-256 key lookup.
    Currently a stub returning None.
    When Redis is wired up, swap the body of lookup() with:

        return await self.redis.get(key)
    """

    async def lookup(self, key: str) -> str | None:
        return None
