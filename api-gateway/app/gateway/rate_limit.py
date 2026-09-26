from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    async def allow(
        self,
        key: str,
        limit: int,
    ) -> bool: ...


class InMemoryRateLimiter(RateLimiter):
    async def allow(self, key, limit):

        return True
