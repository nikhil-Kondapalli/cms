from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class Service:
    name: str
    prefix: str
    url: str


SERVICES = {
    "users": Service(
        name="user-service",
        prefix="users",
        url=settings.user_service_url,
    ),
    "auth": Service(
        name="auth-service",
        prefix="auth",
        url=settings.auth_service_url,
    ),
}
