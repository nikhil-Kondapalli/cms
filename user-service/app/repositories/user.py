from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        stmt = select(User).where(User.email == email)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
        offset: int,
        limit: int,
    ) -> list[User]:

        stmt = (
            select(User)
            .where(User.full_name.ilike(f"%{query}%"))
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
