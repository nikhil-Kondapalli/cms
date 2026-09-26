from typing import Annotated

from fastapi import APIRouter, Depends, status, BackgroundTasks

from app.api.deps import get_auth_service
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.services.auth import AuthService

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    response = await service.login(payload)
    background_tasks.add_task(service.cleanup_expired_tokens)
    return response


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    payload: RefreshTokenRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    response = await service.refresh(payload.refresh_token)
    background_tasks.add_task(service.cleanup_expired_tokens)
    return response


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    payload: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    await service.logout(payload.refresh_token)


@router.post(
    "/forgot-password", status_code=status.HTTP_200_OK
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    await service.forgot_password(payload.email)
    return {"message": "If that email exists, a reset link has been sent."}


@router.post(
    "/reset-password", status_code=status.HTTP_200_OK
)
async def reset_password(
    payload: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    await service.reset_password(payload.token, payload.new_password)
    return {"message": "Password reset successfully."}
