from shared_contracts.auth.schemas import TokenClaims
from shared_contracts.exceptions import AuthorizationError

from app.gateway.routes import Route


class AuthorizationService:
    @staticmethod
    def authorize(
        claims: TokenClaims,
        route: Route,
    ) -> None:

        if not route.required_roles:
            return

        if claims.role not in route.required_roles:
            raise AuthorizationError("Insufficient permissions")
