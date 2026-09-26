from fastapi import Request
from fastapi.responses import JSONResponse
from shared_contracts.exceptions import AuthorizationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.gateway.route_matcher import get_route
from app.services.authorization_service import AuthorizationService


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        route = get_route(
            request.method,
            request.url.path,
        )

        if route is None or route.public:
            return await call_next(request)

        claims = getattr(request.state, "token_claims", None)

        if route.required_roles:
            if claims is None:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Insufficient permissions"},
                )

            try:
                AuthorizationService.authorize(claims, route)
            except AuthorizationError:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Insufficient permissions"},
                )

        return await call_next(request)
