import uuid
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from pydantic import BaseModel, Field


class ExpenseSplitInput(BaseModel):
    user_id: uuid.UUID
    amount: Decimal = Field(gt=0)


class ExpenseBase(BaseModel):
    title: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: str = Field(default="general")
    notes: str | None = None
    occurred_at: datetime | None = None
    splits: Sequence[ExpenseSplitInput]


class ExpenseCreate(ExpenseBase):
    ledger_id: uuid.UUID | None = None


class ExpenseUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    category: str | None = None
    notes: str | None = None
    occurred_at: datetime | None = None
    splits: Sequence[ExpenseSplitInput] | None = None


class ExpenseSplitRead(BaseModel):
    id: str
    user_id: uuid.UUID
    amount: Decimal
    status: str

    class Config:
        orm_mode = True


class ExpenseRead(BaseModel):
    id: uuid.UUID
    ledger_id: uuid.UUID | None
    payer_id: uuid.UUID
    title: str
    amount: Decimal
    currency: str
    category: str
    notes: str | None
    occurred_at: datetime
    created_at: datetime
    splits: list[ExpenseSplitRead]

    class Config:
        orm_mode = True
