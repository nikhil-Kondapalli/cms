from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.gateway.rate_limit import InMemoryRateLimiter
from app.gateway.route_matcher import get_route

limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        route = get_route(
            request.method,
            request.url.path,
        )

        if route is not None and route.rate_limit:

            key = request.client.host if request.client else "unknown"

            allowed = await limiter.allow(
                key,
                route.rate_limit,
            )

            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests",
                )

        return await call_next(request)
