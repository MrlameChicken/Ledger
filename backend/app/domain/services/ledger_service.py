import uuid
from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain import models
from app.schemas.ledger import BalanceEntry, LedgerCreate


def ensure_membership(db: Session, ledger_id: uuid.UUID, user_id: uuid.UUID) -> models.LedgerMembership:
    ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if not ledger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ledger not found")
    membership = (
        db.query(models.LedgerMembership)
        .filter(
            models.LedgerMembership.ledger_id == ledger_id,
            models.LedgerMembership.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this ledger")
    return membership


def create_ledger(db: Session, owner: models.User, data: LedgerCreate) -> models.Ledger:
    ledger = models.Ledger(name=data.name, description=data.description, owner=owner)
    db.add(ledger)
    db.flush()
    membership = models.LedgerMembership(ledger=ledger, user=owner, role="owner")
    db.add(membership)
    db.commit()
    db.refresh(ledger)
    return ledger


def list_ledgers_for_user(db: Session, user: models.User) -> list[models.Ledger]:
    memberships = (
        db.query(models.LedgerMembership)
        .filter(models.LedgerMembership.user_id == user.id)
        .all()
    )
    return [membership.ledger for membership in memberships]


def add_member(db: Session, ledger: models.Ledger, user: models.User, role: str = "member") -> models.LedgerMembership:
    existing = (
        db.query(models.LedgerMembership)
        .filter(
            models.LedgerMembership.ledger_id == ledger.id,
            models.LedgerMembership.user_id == user.id,
        )
        .first()
    )
    if existing:
        return existing
    membership = models.LedgerMembership(ledger=ledger, user=user, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def get_balances(db: Session, ledger_id: uuid.UUID) -> list[BalanceEntry]:
    ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found")
    balances: defaultdict[uuid.UUID, Decimal] = defaultdict(lambda: Decimal("0"))
    for expense in ledger.expenses:
        for split in expense.splits:
            if split.user_id == expense.payer_id:
                continue
            balances[split.user_id] -= Decimal(split.amount)
            balances[expense.payer_id] += Decimal(split.amount)
    return [BalanceEntry(user_id=user_id, balance=balance) for user_id, balance in balances.items()]
