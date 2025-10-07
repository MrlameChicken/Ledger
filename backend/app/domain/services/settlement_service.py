import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain import models
from app.domain.services.ledger_service import ensure_membership
from app.schemas.settlement import SettlementCreate


def create_settlement(db: Session, from_user: models.User, payload: SettlementCreate) -> models.Settlement:
    ensure_membership(db, payload.ledger_id, from_user.id)
    ensure_membership(db, payload.ledger_id, payload.to_user_id)
    settlement = models.Settlement(
        ledger_id=payload.ledger_id,
        from_user_id=from_user.id,
        to_user_id=payload.to_user_id,
        amount=payload.amount,
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement


def confirm_settlement(db: Session, settlement_id: uuid.UUID, user: models.User) -> models.Settlement:
    settlement = db.query(models.Settlement).filter(models.Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if settlement.to_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only recipient can confirm settlement")
    settlement.status = models.SettlementStatus.CONFIRMED.value
    settlement.settled_at = datetime.utcnow()
    db.commit()
    db.refresh(settlement)
    return settlement


def list_settlements(db: Session, ledger_id: uuid.UUID, user: models.User) -> list[models.Settlement]:
    ensure_membership(db, ledger_id, user.id)
    return (
        db.query(models.Settlement)
        .filter(models.Settlement.ledger_id == ledger_id)
        .order_by(models.Settlement.created_at.desc())
        .all()
    )
