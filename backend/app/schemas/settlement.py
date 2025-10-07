import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SettlementCreate(BaseModel):
    ledger_id: uuid.UUID
    to_user_id: uuid.UUID
    amount: Decimal = Field(gt=0)


class SettlementRead(BaseModel):
    id: uuid.UUID
    ledger_id: uuid.UUID
    from_user_id: uuid.UUID
    to_user_id: uuid.UUID
    amount: Decimal
    status: str
    created_at: datetime
    settled_at: datetime | None

    class Config:
        orm_mode = True
