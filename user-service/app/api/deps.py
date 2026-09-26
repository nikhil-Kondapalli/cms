from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared_contracts.auth.jwt_verifier import JWTVerifierService
from shared_contracts.auth.schemas import TokenClaims
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.database import get_db
from app.services.user import UserService

security = HTTPBearer()

jwt_verifier = JWTVerifierService(
    public_key_path=settings.jwt_public_key_path,
    algorithm=settings.jwt_algorithm,
    audience=settings.jwt_audience,
    issuer=settings.jwt_issuer,
)


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    return UserService(session)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
) -> TokenClaims:
    try:
        return jwt_verifier.verify_access_token(credentials.credentials)
    except Exception as e:
        print(f"JWT Verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin_role(
    claims: Annotated[TokenClaims, Depends(get_current_user)],
) -> TokenClaims:
    if claims.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions",
        )
    return claims
