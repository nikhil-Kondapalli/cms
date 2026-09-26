from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.user_service import UserServiceClient
from app.db.session import get_db
from app.repositories.credential import CredentialRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.password_reset_token import PasswordResetTokenRepository
from app.services.auth import AuthService
from app.services.jwt_issuer_service import JWTIssuerService


async def get_user_client():
    client = UserServiceClient()
    try:
        yield client
    finally:
        await client.close()


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_client: Annotated[UserServiceClient, Depends(get_user_client)],
) -> AuthService:
    return AuthService(
        credential_repo=CredentialRepository(session),
        refresh_token_repo=RefreshTokenRepository(session),
        password_reset_token_repo=PasswordResetTokenRepository(session),
        user_client=user_client,
        jwt_issuer=JWTIssuerService(),
    )
