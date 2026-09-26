from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# TYPE_CHECKING is False at runtime but True during static analysis (e.g. Pyright).
# Importing Post here allows type hinting without causing circular import errors.
if TYPE_CHECKING:
    from app.models.post import Post
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Defines a One-to-Many relationship. A single Category can have multiple Posts.
    # back_populates="category" links this to the 'category' attribute defined on the Post model.
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")
