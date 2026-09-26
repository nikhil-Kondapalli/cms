from pathlib import Path
from typing import Literal

import jwt
from jwt import (
    ExpiredSignatureError,
)
from jwt import (
    InvalidTokenError as PyJWTInvalidTokenError,
)
from pydantic import ValidationError

from shared_contracts.auth.schemas import TokenClaims
from shared_contracts.exceptions import (
    InvalidAccessTokenError,
    InvalidTokenError,
    TokenExpiredError,
)


class JWTVerifierService:
    def __init__(
        self,
        public_key_path: str,
        algorithm: str = "RS256",
        audience: str = "cms-api",
        issuer: str = "auth-service",
    ) -> None:
        self._public_key = Path(public_key_path).read_text()
        self.algorithm = algorithm
        self.audience = audience
        self.issuer = issuer

    def verify_token(
        self,
        token: str,
        expected_type: Literal["access", "refresh"],
    ) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )

        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token has expired") from exc

        except PyJWTInvalidTokenError as exc:
            raise InvalidTokenError(f"Invalid token: {exc}") from exc

        if payload.get("type") != expected_type:
            raise InvalidTokenError("Invalid token type")

        try:
            return TokenClaims.model_validate(payload)
        except ValidationError as exc:
            raise InvalidTokenError("Invalid token payload") from exc

    def verify_access_token(self, token: str) -> TokenClaims:
        try:
            return self.verify_token(token, expected_type="access")
        except (InvalidTokenError, TokenExpiredError) as exc:
            raise InvalidAccessTokenError(str(exc)) from exc
