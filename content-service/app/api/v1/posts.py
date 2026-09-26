import re
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from shared_contracts.auth.schemas import TokenClaims

from app.api.deps import (
    get_category_repo,
    get_current_user,
    get_post_repo,
    get_tag_repo,
    require_admin_role,
)
from app.models.post import Post, PostStatus
from app.repositories.category import CategoryRepository
from app.repositories.post import PostRepository
from app.repositories.tag import TagRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.post import PostCreate, PostDetailResponse, PostListResponse, PostUpdate
from app.utils.slug import generate_slug

router = APIRouter()

@router.post(
    "",
    response_model=PostDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post_in: PostCreate,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    post_repo: Annotated[PostRepository, Depends(get_post_repo)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repo)],
    tag_repo: Annotated[TagRepository, Depends(get_tag_repo)],
):
    slug = generate_slug(post_in.title)
    existing = await post_repo.get_by_slug(slug)
    if existing:
        # Append a timestamp to make slug unique if title matches
        slug = f"{slug}-{int(datetime.now().timestamp())}"
        
    post = Post(
        title=post_in.title,
        slug=slug,
        summary=post_in.summary,
        content=post_in.content,
        author_id=current_user.sub,
        category_id=post_in.category_id,
        status=PostStatus.DRAFT,
    )
    
    if post_in.category_id:
        category = await category_repo.get_by_id(post_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
            
    if post_in.tags:
        for tag_id in post_in.tags:
            tag = await tag_repo.get_by_id(tag_id)
            if tag:
                post.tags.append(tag)
                
    post = await post_repo.create(post)
    await post_repo.session.commit()
    # refresh to load relationships correctly for the response
    return await post_repo.get_by_id_with_relations(post.id)


@router.get("", response_model=PaginatedResponse[PostListResponse])
async def list_posts(
    pagination: Annotated[PaginationParams, Depends()],
    post_repo: Annotated[PostRepository, Depends(get_post_repo)],
    status: PostStatus | None = None,
    author_id: UUID | None = None,
    category_id: UUID | None = None,
    tag_id: UUID | None = None,
):
    posts = await post_repo.list_posts(
        offset=pagination.offset,
        limit=pagination.limit,
        status=status,
        author_id=author_id,
        category_id=category_id,
        tag_id=tag_id,
    )
    total = await post_repo.count_posts(
        status=status,
        author_id=author_id,
        category_id=category_id,
        tag_id=tag_id,
    )
    
    return PaginatedResponse.create(
        content=[PostListResponse.model_validate(p) for p in posts],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{slug_or_id}", response_model=PostDetailResponse)
async def get_post(
    slug_or_id: str,
    post_repo: Annotated[PostRepository, Depends(get_post_repo)],
):
    try:
        id_val = UUID(slug_or_id)
        post = await post_repo.get_by_id_with_relations(id_val)
    except ValueError:
        post = await post_repo.get_by_slug(slug_or_id)
        
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    return post


@router.put("/{post_id}", response_model=PostDetailResponse)
async def update_post(
    post_id: UUID,
    post_in: PostUpdate,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    post_repo: Annotated[PostRepository, Depends(get_post_repo)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repo)],
    tag_repo: Annotated[TagRepository, Depends(get_tag_repo)],
):
    post = await post_repo.get_by_id_with_relations(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Only author or admin can edit
    if str(post.author_id) != str(current_user.sub) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")

    if post_in.title is not None:
        post.title = post_in.title
    if post_in.summary is not None:
        post.summary = post_in.summary
    if post_in.content is not None:
        post.content = post_in.content
    if post_in.status is not None:
        post.status = post_in.status
        if post_in.status == PostStatus.PUBLISHED and not post.published_at:
            post.published_at = datetime.now(timezone.utc)
            
    if post_in.category_id is not None:
        category = await category_repo.get_by_id(post_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        post.category_id = post_in.category_id
        
    if post_in.tags is not None:
        post.tags = []
        for tag_id in post_in.tags:
            tag = await tag_repo.get_by_id(tag_id)
            if tag:
                post.tags.append(tag)
                
    await post_repo.session.commit()
    await post_repo.session.refresh(post)
    return await post_repo.get_by_id_with_relations(post.id)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: UUID,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    post_repo: Annotated[PostRepository, Depends(get_post_repo)],
):
    post = await post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if str(post.author_id) != str(current_user.sub) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
    await post_repo.delete(post)
    await post_repo.session.commit()
