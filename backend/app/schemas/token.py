from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
