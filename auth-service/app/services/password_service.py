from pwdlib import PasswordHash


class PasswordService:
    """
    Handles password hashing and verification.

    This service is intentionally stateless. It wraps the password hashing
    library so the rest of the application doesn't depend on a specific
    implementation.
    """

    __password_hash = PasswordHash.recommended()

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a plaintext password using the recommended algorithm (Argon2id).
        """
        return cls.__password_hash.hash(password)

    @classmethod
    def verify_password(
        cls,
        password: str,
        password_hash: str,
    ):
        """
        Verify a plaintext password against a stored hash.
        """
        return cls.__password_hash.verify(password, password_hash)
