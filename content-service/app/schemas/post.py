from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.post import PostStatus
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    summary: str | None = None
    category_id: UUID | None = None


class PostCreate(PostBase):
    content: str
    tags: list[UUID] = Field(default_factory=list)


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    summary: str | None = None
    content: str | None = None
    status: PostStatus | None = None
    category_id: UUID | None = None
    tags: list[UUID] | None = None


class PostListResponse(PostBase):
    """
    Thin payload for list views. Excludes 'content' to save bandwidth.
    """
    id: UUID
    slug: str
    status: PostStatus
    author_id: UUID
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostListResponse):
    """
    Rich payload for detail views. Includes heavy 'content' body and nested relationships.
    """
    content: str
    category: CategoryResponse | None = None
    tags: list[TagResponse] = Field(default_factory=list)
