from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.infrastructure.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = Column(String(255), nullable=False)
    full_name: Mapped[str | None] = Column(String(255), nullable=True)
    timezone: Mapped[str | None] = Column(String(64), nullable=True)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    ledgers_owned: Mapped[list["Ledger"]] = relationship("Ledger", back_populates="owner")
    memberships: Mapped[list["LedgerMembership"]] = relationship(
        "LedgerMembership", back_populates="user", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="payer")


class Ledger(Base):
    __tablename__ = "ledgers"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str | None] = Column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="ledgers_owned")
    members: Mapped[list["LedgerMembership"]] = relationship(
        "LedgerMembership", back_populates="ledger", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="ledger", cascade="all, delete-orphan"
    )
    settlements: Mapped[list["Settlement"]] = relationship(
        "Settlement", back_populates="ledger", cascade="all, delete-orphan"
    )


class LedgerMembership(Base):
    __tablename__ = "ledger_members"
    __table_args__ = (
        UniqueConstraint("ledger_id", "user_id", name="uq_ledger_member"),
    )

    ledger_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("ledgers.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    role: Mapped[str] = Column(String(32), default="member", nullable=False)
    joined_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    ledger: Mapped[Ledger] = relationship("Ledger", back_populates="members")
    user: Mapped[User] = relationship("User", back_populates="memberships")


class ExpenseCategory(str, Enum):
    GENERAL = "general"
    FOOD = "food"
    TRAVEL = "travel"
    HOUSING = "housing"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ledger_id: Mapped[uuid.UUID | None] = Column(UUID(as_uuid=True), ForeignKey("ledgers.id"), nullable=True)
    payer_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    amount: Mapped[Decimal] = Column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = Column(String(3), nullable=False, default="USD")
    category: Mapped[str] = Column(String(64), nullable=False, default=ExpenseCategory.GENERAL.value)
    notes: Mapped[str | None] = Column(Text, nullable=True)
    occurred_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    ledger: Mapped[Ledger | None] = relationship("Ledger", back_populates="expenses")
    payer: Mapped[User] = relationship("User", back_populates="expenses")
    splits: Mapped[list["ExpenseSplit"]] = relationship(
        "ExpenseSplit", back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id: Mapped[str] = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    expense_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = Column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = Column(String(32), default="open", nullable=False)

    expense: Mapped[Expense] = relationship("Expense", back_populates="splits")
    user: Mapped[User] = relationship("User")


class SettlementStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ledger_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("ledgers.id"), nullable=False)
    from_user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = Column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = Column(String(32), default=SettlementStatus.PENDING.value, nullable=False)
    settled_at: Mapped[datetime | None] = Column(DateTime, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    ledger: Mapped[Ledger] = relationship("Ledger", back_populates="settlements")
    from_user: Mapped[User] = relationship("User", foreign_keys=[from_user_id])
    to_user: Mapped[User] = relationship("User", foreign_keys=[to_user_id])
