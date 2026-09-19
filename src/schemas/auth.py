from pydantic import Field

from schemas.base import CamelModel


class LoginRequest(CamelModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1)


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
