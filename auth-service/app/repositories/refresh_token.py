from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def update(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def delete(self, token: RefreshToken) -> None:
        await self.session.delete(token)
        await self.session.flush()

    async def delete_expired(self) -> None:
        from sqlalchemy import delete

        stmt = delete(RefreshToken).where(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        )
        await self.session.execute(stmt)
        await self.session.flush()
