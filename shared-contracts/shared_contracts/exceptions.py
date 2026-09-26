class InvalidTokenError(Exception):
    """Raised when JWT validation fails."""


class InvalidAccessTokenError(InvalidTokenError):
    """Raised when access token validation fails."""


class InvalidCredentialsError(Exception):
    """Raised for incorrect username/password."""


class TokenExpiredError(Exception):
    """Raised when JWT has expired."""


class AuthorizationError(Exception):
    """Raised when an authenticated user is not authorized."""
