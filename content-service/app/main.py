from fastapi import FastAPI

from app.api.router import api_router
from app.core.handlers import register_exception_handlers
from app.core.lifespan import lifespan

app = FastAPI(
    title="Content Service",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
