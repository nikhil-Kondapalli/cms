from typing import TYPE_CHECKING
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.category import Category
from app.models.tag import Tag


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Post(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    
    status: Mapped[PostStatus] = mapped_column(
        SQLEnum(PostStatus, name="poststatus", create_type=False),
        default=PostStatus.DRAFT,
        index=True,
    )
    
    author_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    # ondelete="SET NULL" ensures that if a Category is deleted, the posts in that category
    # are NOT deleted. Instead, their category_id is safely set to NULL.
    category_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    category: Mapped["Category | None"] = relationship("Category", back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="post_tags",
        back_populates="posts",
    )
    # cascade="all, delete-orphan" operates at the SQLAlchemy ORM level (not DB level).
    # If a Comment is removed from the `post.comments` list in Python, SQLAlchemy deletes it from the DB.
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )
