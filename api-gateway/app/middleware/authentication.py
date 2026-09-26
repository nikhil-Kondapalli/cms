from fastapi import Request
from fastapi.responses import JSONResponse
from shared_contracts.auth.jwt_verifier import JWTVerifierService
from shared_contracts.exceptions import InvalidAccessTokenError
from starlette.middleware.base import BaseHTTPMiddleware

from app.gateway.route_matcher import get_route


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        jwt_verifier: JWTVerifierService,
    ):
        super().__init__(app)
        self.jwt_verifier = jwt_verifier

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

        authorization = request.headers.get("Authorization")

        if authorization is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"},
            )

        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer" or not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication scheme"},
            )

        try:
            claims = self.jwt_verifier.verify_access_token(token)
        except InvalidAccessTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired access token"},
            )

        # Authentication succeeded
        request.state.token_claims = claims
        request.state.user_id = claims.sub

        return await call_next(request)
