from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from shared_contracts.auth.schemas import TokenClaims

from app.api.deps import get_comment_repo, get_current_user, require_admin_role
from app.models.comment import Comment, CommentStatus
from app.repositories.comment import CommentRepository
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()

@router.post(
    "/post/{post_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: UUID,
    comment_in: CommentCreate,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    repo: Annotated[CommentRepository, Depends(get_comment_repo)],
):
    comment = Comment(
        post_id=post_id,
        author_id=current_user.sub,
        content=comment_in.content,
        status=CommentStatus.PENDING,
    )
    # Auto-approve admin comments
    if current_user.role == "admin":
        comment.status = CommentStatus.APPROVED
        
    comment = await repo.create(comment)
    await repo.session.commit()
    return comment


@router.get(
    "/post/{post_id}",
    response_model=PaginatedResponse[CommentResponse]
)
async def list_comments_for_post(
    post_id: UUID,
    pagination: Annotated[PaginationParams, Depends()],
    repo: Annotated[CommentRepository, Depends(get_comment_repo)],
):
    # Public API only lists approved comments
    comments = await repo.list_by_post(
        post_id=post_id,
        offset=pagination.offset,
        limit=pagination.limit,
        status=CommentStatus.APPROVED,
    )
    total = await repo.count_by_post(
        post_id=post_id,
        status=CommentStatus.APPROVED,
    )
    
    return PaginatedResponse.create(
        content=[CommentResponse.model_validate(c) for c in comments],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.put(
    "/{comment_id}/status",
    response_model=CommentResponse,
    dependencies=[Depends(require_admin_role)],
)
async def update_comment_status(
    comment_id: UUID,
    comment_in: CommentUpdate,
    repo: Annotated[CommentRepository, Depends(get_comment_repo)],
):
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    comment.status = comment_in.status
    await repo.session.commit()
    await repo.session.refresh(comment)
    return comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: UUID,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    repo: Annotated[CommentRepository, Depends(get_comment_repo)],
):
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if str(comment.author_id) != str(current_user.sub) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
    await repo.delete(comment)
    await repo.session.commit()
