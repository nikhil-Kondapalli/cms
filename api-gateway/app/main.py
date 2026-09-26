from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared_contracts.auth.jwt_verifier import JWTVerifierService

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.middleware.authentication import AuthenticationMiddleware
from app.middleware.authorization import AuthorizationMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.routers.gateway import router as gateway_router
from app.routers.health import router as health_router

jwt_verifier = JWTVerifierService(
    public_key_path=settings.jwt_public_key_path,
    algorithm=settings.jwt_algorithm,
    audience=settings.jwt_audience,
    issuer=settings.jwt_issuer,
)

setup_logging()

app = FastAPI(
    title="API Gateway",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(gateway_router)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuthorizationMiddleware)
app.add_middleware(AuthenticationMiddleware, jwt_verifier=jwt_verifier)
app.add_middleware(RateLimitMiddleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.port,
        reload=settings.debug,
    )
