import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class LedgerBase(BaseModel):
    name: str
    description: str | None = None


class LedgerCreate(LedgerBase):
    pass


class LedgerUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class LedgerRead(LedgerBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True


class LedgerMemberRead(BaseModel):
    user: UserRead
    role: str
    joined_at: datetime


class BalanceEntry(BaseModel):
    user_id: uuid.UUID
    balance: Decimal = Field(..., description="Positive means others owe this user")
