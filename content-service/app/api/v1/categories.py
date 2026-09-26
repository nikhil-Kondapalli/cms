from app.api.deps import get_category_service
from app.services.category_service import CategoryService
import re
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from shared_contracts.auth.schemas import TokenClaims

from app.api.deps import get_category_repo, get_current_user, require_admin_role
from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.utils.slug import generate_slug

router = APIRouter()


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_role)],
)
async def create_category(
    payload: CategoryCreateRequest,
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    return await service.create(payload)


@router.get("", response_model=PaginatedResponse[CategoryResponse])
async def list_categories(
    pagination: Annotated[PaginationParams, Depends()],
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
    categories = await repo.list(offset=pagination.offset, limit=pagination.limit)
    total = await repo.count()
    return PaginatedResponse.create(
        content=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_admin_role)],
)
async def update_category(
    category_id: UUID,
    category_in: CategoryUpdateRequest,
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category_in.name is not None:
        category.name = category_in.name
        new_slug = generate_slug(category_in.name)
        if new_slug != category.slug:
            existing = await repo.get_by_slug(new_slug)
            if existing:
                raise HTTPException(
                    status_code=400, detail="Category with this name already exists"
                )
            category.slug = new_slug

    if category_in.description is not None:
        category.description = category_in.description

    await repo.session.commit()
    await repo.session.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_role)],
)
async def delete_category(
    category_id: UUID,
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await repo.delete(category)
    await repo.session.commit()
