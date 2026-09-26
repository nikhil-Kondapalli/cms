from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credential import Credential


class CredentialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Credential | None:
        stmt = select(Credential).where(Credential.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, credential: Credential) -> Credential:
        self.session.add(credential)
        await self.session.flush()
        return credential

    async def update(self, credential: Credential) -> Credential:
        self.session.add(credential)
        await self.session.flush()
        return credential
