from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.comment import Comment, CommentStatus
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Comment)

    async def list_by_post(
        self,
        post_id: UUID,
        offset: int = 0,
        limit: int = 20,
        status: CommentStatus | None = CommentStatus.APPROVED,
    ) -> list[Comment]:
        stmt = select(Comment).where(Comment.post_id == post_id)
        
        if status:
            stmt = stmt.where(Comment.status == status)
            
        stmt = stmt.order_by(Comment.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_post(
        self,
        post_id: UUID,
        status: CommentStatus | None = CommentStatus.APPROVED,
    ) -> int:
        stmt = select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        
        if status:
            stmt = stmt.where(Comment.status == status)
            
        result = await self.session.execute(stmt)
        return result.scalar_one()
