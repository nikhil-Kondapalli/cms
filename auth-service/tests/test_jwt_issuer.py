from pathlib import Path
from uuid import uuid4

import jwt

from app.core.config import settings
from app.services.jwt_issuer_service import JWTIssuerService


def test_jwt_issuer_create_access_token():
    issuer = JWTIssuerService()
    user_id = uuid4()
    role = "admin"

    token = issuer.create_access_token(subject=user_id, role=role)
    assert token is not None

    public_key = Path(settings.jwt_public_key_path).read_text()
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )

    assert payload["sub"] == str(user_id)
    assert payload["role"] == role
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "iat" in payload
    assert "exp" in payload


def test_jwt_issuer_create_refresh_token():
    issuer = JWTIssuerService()
    user_id = uuid4()
    role = "user"

    token = issuer.create_refresh_token(subject=user_id, role=role)
    assert token is not None

    public_key = Path(settings.jwt_public_key_path).read_text()
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )

    assert payload["sub"] == str(user_id)
    assert payload["role"] == role
    assert payload["type"] == "refresh"
