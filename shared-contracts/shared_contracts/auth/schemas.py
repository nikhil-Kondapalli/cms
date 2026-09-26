from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenClaims(BaseModel):
    sub: UUID
    type: str
    role: str
    iss: str
    aud: str
    iat: datetime
    exp: datetime
    jti: UUID
