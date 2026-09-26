from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
)

app.include_router(health_router)
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn

    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=getattr(settings, "debug", False),
    )
