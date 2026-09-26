from collections.abc import Sequence
from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    content: Sequence[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        *,
        content: Sequence[T],
        total: int,
        page: int,
        page_size: int,
    ):
        pages = ceil(total / page_size) if total else 0

        return cls(
            content=content,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_previous=page > 1,
        )
