from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from shared_contracts.auth.schemas import TokenClaims

from app.api.deps import get_current_user, get_user_service, require_admin_role
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(
    payload: UserCreate,
    service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    user = await service.create_user(payload)
    return UserResponse.model_validate(user)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_user_profile(
    claims: Annotated[TokenClaims, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = await service.get_user(claims.sub)
    return UserResponse.model_validate(user)


@router.put(
    "/me",
    response_model=UserResponse,
)
async def update_current_user_profile(
    payload: UserUpdate,
    claims: Annotated[TokenClaims, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    # Only allow updating own full_name here, filter payload if needed
    safe_payload = UserUpdate(full_name=payload.full_name)
    user = await service.update_user(claims.sub, safe_payload)
    return UserResponse.model_validate(user)


@router.get(
    "/by-email",
    response_model=UserResponse,
)
async def get_user_by_email(
    email: str,
    service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    user = await service.get_user_by_email(email)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.get(
    "/search",
    response_model=list[UserResponse],
)
async def search_users(
    q: str,
    service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
    page: int = 1,
    page_size: int = 20,
):

    pagination = PaginationParams(
        page=page,
        page_size=page_size,
    )

    return await service.search_users(
        q,
        pagination,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID,
    service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    user = await service.get_user(user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    claims: Annotated[TokenClaims, Depends(require_admin_role)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = await service.update_user(user_id, payload)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
)
async def list_users(
    service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):

    pagination = PaginationParams(
        page=page,
        page_size=page_size,
    )

    return await service.list_users(pagination)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):

    await service.delete_user(user_id)
