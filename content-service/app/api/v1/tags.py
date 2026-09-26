import re
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from shared_contracts.auth.schemas import TokenClaims

from app.api.deps import get_tag_repo, require_admin_role
from app.models.tag import Tag
from app.repositories.tag import TagRepository
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.common import PaginatedResponse, PaginationParams
from app.utils.slug import generate_slug

router = APIRouter()

@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_role)],
)
async def create_tag(
    tag_in: TagCreate,
    repo: Annotated[TagRepository, Depends(get_tag_repo)],
):
    slug = generate_slug(tag_in.name)
    existing = await repo.get_by_slug(slug)
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
        
    tag = Tag(name=tag_in.name, slug=slug)
    tag = await repo.create(tag)
    await repo.session.commit()
    return tag


@router.get("", response_model=PaginatedResponse[TagResponse])
async def list_tags(
    pagination: Annotated[PaginationParams, Depends()],
    repo: Annotated[TagRepository, Depends(get_tag_repo)],
):
    tags = await repo.list(offset=pagination.offset, limit=pagination.limit)
    total = await repo.count()
    return PaginatedResponse.create(
        content=[TagResponse.model_validate(t) for t in tags],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_role)],
)
async def delete_tag(
    tag_id: UUID,
    repo: Annotated[TagRepository, Depends(get_tag_repo)],
):
    tag = await repo.get_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    await repo.delete(tag)
    await repo.session.commit()
