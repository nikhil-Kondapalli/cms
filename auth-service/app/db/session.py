from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

# The Engine is a factory that manages connections.
# This does not connect to PostgreSQL immediately.
# It creates an Engine object that knows:
# Database URL
# Driver
# Pool configuration
# The actual network connection is usually established lazily when the first database operation occurs.

engine = create_async_engine(
    settings.database_url,
    echo=True,
)

# SessionLocal is a Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# SQLAlchemy can sometimes send pending changes to the database before a query executes (this is called a flush).
# autoFlush=False Those automatic flushes are disabled. We choose when changes are flushed or committed, which makes behavior easier to understand while learning.

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
