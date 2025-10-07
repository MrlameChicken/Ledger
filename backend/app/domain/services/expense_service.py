import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain import models
from app.domain.services.ledger_service import ensure_membership
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, payer: models.User, payload: ExpenseCreate) -> models.Expense:
    if payload.ledger_id:
        ensure_membership(db, payload.ledger_id, payer.id)
        for split in payload.splits:
            ensure_membership(db, payload.ledger_id, split.user_id)
    total_split = sum(split.amount for split in payload.splits)
    if Decimal(payload.amount) != Decimal(total_split):
        raise HTTPException(status_code=400, detail="Split amounts must equal total amount")
    expense = models.Expense(
        ledger_id=payload.ledger_id,
        payer_id=payer.id,
        title=payload.title,
        amount=payload.amount,
        currency=payload.currency,
        category=payload.category,
        notes=payload.notes,
        occurred_at=payload.occurred_at or datetime.utcnow(),
    )
    db.add(expense)
    db.flush()
    for split in payload.splits:
        db.add(
            models.ExpenseSplit(
                expense_id=expense.id,
                user_id=split.user_id,
                amount=split.amount,
            )
        )
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(db: Session, ledger_id: uuid.UUID | None, user: models.User) -> list[models.Expense]:
    query = db.query(models.Expense)
    if ledger_id:
        ensure_membership(db, ledger_id, user.id)
        query = query.filter(models.Expense.ledger_id == ledger_id)
    else:
        query = query.filter(models.Expense.ledger_id.is_(None), models.Expense.payer_id == user.id)
    return query.order_by(models.Expense.occurred_at.desc()).all()


def update_expense(db: Session, expense_id: uuid.UUID, user: models.User, payload: ExpenseUpdate) -> models.Expense:
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.payer_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only payer can update expense")
    for field, value in payload.dict(exclude_unset=True).items():
        if field == "splits" and value is not None:
            total_split = sum(split.amount for split in value)
            if Decimal(expense.amount if payload.amount is None else payload.amount) != Decimal(total_split):
                raise HTTPException(status_code=400, detail="Split amounts must equal total amount")
            if expense.ledger_id:
                for split in value:
                    ensure_membership(db, expense.ledger_id, split.user_id)
            for existing in list(expense.splits):
                db.delete(existing)
            for split in value:
                db.add(
                    models.ExpenseSplit(
                        expense_id=expense.id,
                        user_id=split.user_id,
                        amount=split.amount,
                    )
                )
        elif field == "occurred_at" and value is None:
            continue
        elif hasattr(expense, field):
            setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: uuid.UUID, user: models.User) -> None:
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.payer_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only payer can delete expense")
    db.delete(expense)
    db.commit()
