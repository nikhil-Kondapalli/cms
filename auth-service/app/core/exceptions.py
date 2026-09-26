class InvalidTokenError(Exception):
    """Raised when JWT validation fails."""


class InvalidCredentialsError(Exception):
    """Raised for incorrect username/password."""


class TokenExpiredError(Exception):
    """Raised when JWT has expired."""
