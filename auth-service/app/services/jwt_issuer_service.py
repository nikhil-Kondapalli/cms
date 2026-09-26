from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import jwt

from app.core.config import settings


class JWTIssuerService:
    """
    Handles JWT creation and verification.

    The RSA keys are loaded once during initialization and
    reused for every request.
    """

    def __init__(self) -> None:
        self._private_key = Path(settings.jwt_private_key_path).read_text()

        # self._public_key = Path(settings.jwt_public_key_path).read_text()

    def _create_token(
        self,
        *,
        subject: UUID,
        token_type: str,
        expires_delta: timedelta,
        role: str,
    ) -> str:
        now = datetime.now(UTC)
        expires_at = now + expires_delta

        payload = {
            "sub": str(subject),
            "type": token_type,
            "role": role,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "iat": now,
            "exp": expires_at,
            "jti": str(uuid4()),
        }

        return jwt.encode(
            payload,
            self._private_key,
            algorithm=settings.jwt_algorithm,
        )

    def create_access_token(
        self,
        *,
        subject: UUID,
        role: str,
    ) -> str:
        return self._create_token(
            subject=subject,
            token_type="access",
            role=role,
            expires_delta=timedelta(
                minutes=settings.access_token_expire_minutes,
            ),
        )

    def create_refresh_token(
        self,
        *,
        subject: UUID,
        role: str,
    ) -> str:
        return self._create_token(
            subject=subject,
            token_type="refresh",
            role=role,
            expires_delta=timedelta(
                days=settings.refresh_token_expire_days,
            ),
        )
