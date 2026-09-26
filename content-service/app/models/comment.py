from typing import TYPE_CHECKING
from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.post import Post
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SPAM = "spam"
    DELETED = "deleted"


class Comment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "comments"

    # ondelete="CASCADE" is a DB-level constraint: if the parent Post is deleted,
    # PostgreSQL automatically deletes all comments associated with it.
    post_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    
    content: Mapped[str] = mapped_column(Text)
    
    # Maps Python Enum to a native ENUM type in PostgreSQL named "commentstatus".
    # create_type=False tells SQLAlchemy that Alembic will handle creating the ENUM type.
    status: Mapped[CommentStatus] = mapped_column(
        SQLEnum(CommentStatus, name="commentstatus", create_type=False),
        default=CommentStatus.PENDING,
        index=True,
    )

    # Defines the Many-to-One side of the relationship (many comments belong to one Post).
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
