from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import jwt
import pytest
from shared_contracts.exceptions import AuthorizationError, InvalidAccessTokenError
from shared_contracts.auth.schemas import TokenClaims
from shared_contracts.auth.jwt_verifier import JWTVerifierService
from fastapi.testclient import TestClient

from app.core.config import settings
from app.gateway.route_matcher import get_route
from app.gateway.routes import Route
from app.main import app
from app.services.authorization_service import AuthorizationService

# Path to private key in auth-service for test token creation
AUTH_PRIVATE_KEY_PATH = (
    Path(__file__).parent.parent.parent / "auth-service" / "keys" / "private.pem"
)


def create_test_token(
    *,
    subject=None,
    role: str = "user",
    token_type: str = "access",
    expired: bool = False,
) -> str:
    private_key = AUTH_PRIVATE_KEY_PATH.read_text()
    now = datetime.now(UTC)
    exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    sub = subject or uuid4()

    payload = {
        "sub": str(sub),
        "type": token_type,
        "role": role,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": exp,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, private_key, algorithm=settings.jwt_algorithm)


def test_token_claims_schema():
    user_id = uuid4()
    jti = uuid4()
    claims = TokenClaims(
        sub=user_id,
        type="access",
        role="admin",
        iss="cms-auth-service",
        aud="cms-api",
        iat=datetime.now(UTC),
        exp=datetime.now(UTC) + timedelta(minutes=15),
        jti=jti,
    )
    assert claims.role == "admin"
    assert claims.sub == user_id
    assert claims.type == "access"


def test_route_matcher():
    # Exact match
    route = get_route("GET", "/health")
    assert route is not None
    assert route.public is True

    # Auth routes
    login_route = get_route("POST", "/auth/login")
    assert login_route is not None
    assert login_route.public is True

    # Parametric route
    user_id = uuid4()
    delete_route = get_route("DELETE", f"/users/{user_id}")
    assert delete_route is not None
    assert "admin" in delete_route.required_roles

    # Multi-role route
    me_route = get_route("GET", "/users/me")
    assert me_route is not None
    assert me_route.required_roles == {"user", "admin"}

    # Unmatched route
    unknown = get_route("GET", "/unknown/route")
    assert unknown is None


def test_authorization_service():
    user_id = uuid4()
    claims_user = TokenClaims(
        sub=user_id,
        type="access",
        role="user",
        iss=settings.jwt_issuer,
        aud=settings.jwt_audience,
        iat=datetime.now(UTC),
        exp=datetime.now(UTC) + timedelta(hours=1),
        jti=uuid4(),
    )
    claims_admin = TokenClaims(
        sub=user_id,
        type="access",
        role="admin",
        iss=settings.jwt_issuer,
        aud=settings.jwt_audience,
        iat=datetime.now(UTC),
        exp=datetime.now(UTC) + timedelta(hours=1),
        jti=uuid4(),
    )

    admin_only_route = Route(
        method="GET",
        path="/users",
        service="user-service",
        required_roles={"admin"},
    )
    user_or_admin_route = Route(
        method="GET",
        path="/users/me",
        service="user-service",
        required_roles={"user", "admin"},
    )
    public_route = Route(
        method="GET",
        path="/health",
        service="api-gateway",
        public=True,
    )

    # Public / No required roles should pass
    AuthorizationService.authorize(claims_user, public_route)

    # User accessing user_or_admin route should pass
    AuthorizationService.authorize(claims_user, user_or_admin_route)

    # Admin accessing user_or_admin route should pass
    AuthorizationService.authorize(claims_admin, user_or_admin_route)

    # Admin accessing admin_only route should pass
    AuthorizationService.authorize(claims_admin, admin_only_route)

    # User accessing admin_only route should raise AuthorizationError
    with pytest.raises(AuthorizationError):
        AuthorizationService.authorize(claims_user, admin_only_route)


def test_jwt_verifier_service():
    verifier = JWTVerifierService(
        public_key_path=settings.jwt_public_key_path,
        algorithm=settings.jwt_algorithm,
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )
    token = create_test_token(role="admin")
    claims = verifier.verify_access_token(token)
    assert claims.role == "admin"

    expired_token = create_test_token(role="admin", expired=True)
    with pytest.raises(InvalidAccessTokenError):
        verifier.verify_access_token(expired_token)


def test_authentication_middleware_flow():
    with TestClient(app) as client:
        # 1. Public route succeeds without auth
        response = client.get("/health")
        assert response.status_code == 200

        # 2. Protected route without header -> 401
        response = client.get("/users/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Missing Authorization header"

        # 3. Invalid auth scheme -> 401
        response = client.get("/users/me", headers={"Authorization": "Basic 123"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication scheme"

        # 4. Expired / Invalid token -> 401
        expired_token = create_test_token(role="user", expired=True)
        response = client.get(
            "/users/me", headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired access token"

        # 5. Valid user token on admin-only route (/users) -> 403 Forbidden
        user_token = create_test_token(role="user")
        response = client.get("/users", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Insufficient permissions"

        # 6. Valid admin token on admin-only route (/users) -> passes auth/authz (reaches route handler/proxy)
        admin_token = create_test_token(role="admin")
        response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
        # The request passed through AuthenticationMiddleware (status won't be 401 or 403)
        assert response.status_code not in (401, 403)
