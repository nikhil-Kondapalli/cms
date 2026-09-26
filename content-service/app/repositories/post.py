from uuid import UUID
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.post import Post, PostStatus
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Post)

    async def get_by_slug(self, slug: str) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.slug == slug)
            .options(selectinload(Post.category), selectinload(Post.tags))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_by_id_with_relations(self, id: UUID) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.id == id)
            .options(selectinload(Post.category), selectinload(Post.tags))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        offset: int = 0,
        limit: int = 20,
        status: PostStatus | None = None,
        author_id: UUID | None = None,
        category_id: UUID | None = None,
        tag_id: UUID | None = None,
    ) -> list[Post]:
        stmt = select(Post)
        
        if status:
            stmt = stmt.where(Post.status == status)
        if author_id:
            stmt = stmt.where(Post.author_id == author_id)
        if category_id:
            stmt = stmt.where(Post.category_id == category_id)
        if tag_id:
            # We need to join with post_tags if we want to filter by tag
            from app.models.post_tag import PostTag
            stmt = stmt.join(PostTag).where(PostTag.tag_id == tag_id)
            
        # For list views, we do NOT load relations to keep payloads thin.
        stmt = stmt.order_by(Post.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_posts(
        self,
        status: PostStatus | None = None,
        author_id: UUID | None = None,
        category_id: UUID | None = None,
        tag_id: UUID | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Post)
        
        if status:
            stmt = stmt.where(Post.status == status)
        if author_id:
            stmt = stmt.where(Post.author_id == author_id)
        if category_id:
            stmt = stmt.where(Post.category_id == category_id)
        if tag_id:
            from app.models.post_tag import PostTag
            stmt = stmt.join(PostTag).where(PostTag.tag_id == tag_id)
            
        result = await self.session.execute(stmt)
        return result.scalar_one()
