import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException

from app.clients.user_service import UserServiceClient
from app.core.config import settings
from app.models.credential import Credential
from app.models.refresh_token import RefreshToken
from app.repositories.credential import CredentialRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.models.password_reset_token import PasswordResetToken
from app.repositories.password_reset_token import PasswordResetTokenRepository
from app.services.jwt_issuer_service import JWTIssuerService
from app.services.password_service import PasswordService


class AuthService:
    def __init__(
        self,
        credential_repo: CredentialRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_reset_token_repo: PasswordResetTokenRepository,
        user_client: UserServiceClient,
        jwt_issuer: JWTIssuerService,
    ):
        self.credential_repo = credential_repo
        self.refresh_token_repo = refresh_token_repo
        self.password_reset_token_repo = password_reset_token_repo
        self.user_client = user_client
        self.jwt_issuer = jwt_issuer

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def register(self, payload: RegisterRequest) -> TokenResponse:
        # Check if email exists in user-service
        existing_user = await self.user_client.get_user_by_email(payload.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user in user-service
        user_data = await self.user_client.create_user(
            email=payload.email,
            full_name=payload.full_name,
        )
        user_id = UUID(user_data["id"])

        # Create credential
        hashed_password = PasswordService.hash_password(payload.password)
        credential = Credential(
            user_id=user_id,
            password_hash=hashed_password,
        )
        await self.credential_repo.create(credential)
        await self.credential_repo.session.commit()

        # Generate tokens using role from user-service response
        role = user_data.get("role", "user")
        return await self._generate_token_response(user_id, role)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user_data = await self.user_client.get_user_by_email(payload.email)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = UUID(user_data["id"])
        credential = await self.credential_repo.get_by_user_id(user_id)

        if not credential:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not PasswordService.verify_password(
            payload.password, credential.password_hash
        ):
            # Increment failed attempts logic here (omitted for brevity)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Fetch role directly from user-service payload
        role = user_data.get("role", "user")

        return await self._generate_token_response(user_id, role)

    async def _generate_token_response(self, user_id: UUID, role: str) -> TokenResponse:
        access_token = self.jwt_issuer.create_access_token(subject=user_id, role=role)
        refresh_token = self.jwt_issuer.create_refresh_token(subject=user_id, role=role)

        token_hash = self._hash_token(refresh_token)
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days
        )

        rt_record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.refresh_token_repo.create(rt_record)
        await self.refresh_token_repo.session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        token_hash = self._hash_token(refresh_token)
        record = await self.refresh_token_repo.get_by_token_hash(token_hash)

        if not record or record.revoked or record.expires_at < datetime.now(UTC):
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        record.revoked = True
        await self.refresh_token_repo.update(record)
        await self.refresh_token_repo.session.commit()

        # In a real app we decode the refresh token to get the subject and role
        import jwt

        try:
            payload = jwt.decode(
                refresh_token,
                Path(settings.jwt_public_key_path).read_text(),
                algorithms=[settings.jwt_algorithm],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
            )
            user_id = UUID(payload["sub"])
            role = payload.get("role", "user")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        return await self._generate_token_response(user_id, role)

    async def logout(self, refresh_token: str) -> None:
        token_hash = self._hash_token(refresh_token)
        record = await self.refresh_token_repo.get_by_token_hash(token_hash)
        if record:
            await self.refresh_token_repo.delete(record)
            await self.refresh_token_repo.session.commit()

    async def cleanup_expired_tokens(self) -> None:
        if settings.enable_opportunistic_cleanup:
            await self.refresh_token_repo.delete_expired()
            await self.refresh_token_repo.session.commit()

    async def forgot_password(self, email: str) -> None:
        import secrets

        user_data = await self.user_client.get_user_by_email(email)
        # Security: Return silently if user not found to prevent email enumeration
        if not user_data:
            return

        user_id = UUID(user_data["id"])
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)

        expires_at = datetime.now(UTC) + timedelta(minutes=30)

        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        await self.password_reset_token_repo.create(reset_token)
        await self.password_reset_token_repo.session.commit()

        # Placeholder for actual email sending logic
        print(
            f"\n--- FORGOT PASSWORD ---\nUser: {email}\nReset Link: https://frontend.com/reset-password?token={raw_token}\n-----------------------\n"
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        token_hash = self._hash_token(token)
        reset_record = await self.password_reset_token_repo.get_valid_by_token_hash(
            token_hash
        )

        if not reset_record:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )

        # Update user's credential
        credential = await self.credential_repo.get_by_user_id(reset_record.user_id)
        if not credential:
            raise HTTPException(status_code=400, detail="User credentials not found")

        credential.password_hash = PasswordService.hash_password(new_password)
        credential.password_changed_at = datetime.now(UTC)

        # Mark token as used
        reset_record.used = True

        # Revoke all existing refresh tokens for security
        await self.refresh_token_repo.revoke_all_for_user(reset_record.user_id)

        await self.credential_repo.session.commit()
