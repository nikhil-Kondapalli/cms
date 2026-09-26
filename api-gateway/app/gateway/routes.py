from dataclasses import dataclass, field


@dataclass
class Route:
    method: str
    path: str
    service: str
    public: bool = False
    required_roles: set[str] = field(default_factory=set)
    rate_limit: int = 0


routes = [
    Route(
        method="GET",
        path="/api/v1/health",
        service="api-gateway",
        public=True,
    ),
    Route(
        method="POST",
        path="/api/v1/auth/login",
        service="auth",
        public=True,
    ),
    Route(
        method="POST",
        path="/api/v1/auth/refresh",
        service="auth",
        public=True,
    ),
    Route(
        method="POST",
        path="/api/v1/auth/register",
        service="auth",
        public=True,
    ),
    Route(
        method="POST",
        path="/api/v1/auth/logout",
        service="auth",
        required_roles={"user", "admin"},
    ),
    Route(
        method="POST",
        path="/api/v1/auth/password/change",
        service="auth",
        required_roles={"user", "admin"},
    ),
    Route(
        method="GET",
        path="/api/v1/users/me",
        service="users",
        required_roles={"user", "admin"},
    ),
    Route(
        method="GET",
        path="/api/v1/users",
        service="users",
        required_roles={"admin"},
    ),
    Route(
        method="GET",
        path="/api/v1/users/search",
        service="users",
        required_roles={"admin"},
    ),
    Route(
        method="GET",
        path="/api/v1/users/{user_id}",
        service="users",
        required_roles={"user", "admin"},
    ),
    Route(
        method="DELETE",
        path="/api/v1/users/{user_id}",
        service="users",
        required_roles={"admin"},
    ),
    Route(
        method="PUT",
        path="/api/v1/users/me",
        service="users",
        required_roles={"user", "admin"},
    ),
    Route(
        method="PATCH",
        path="/api/v1/users/{user_id}",
        service="users",
        required_roles={"admin"},
    ),
]
