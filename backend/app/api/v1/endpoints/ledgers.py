import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.domain import models
from app.domain.services import ledger_service
from app.schemas.ledger import BalanceEntry, LedgerCreate, LedgerRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/ledgers", tags=["ledgers"])


@router.get("/", response_model=list[LedgerRead])
def list_ledgers(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> list[LedgerRead]:
    ledgers = ledger_service.list_ledgers_for_user(db, current_user)
    return [LedgerRead.from_orm(ledger) for ledger in ledgers]


@router.post("/", response_model=LedgerRead, status_code=status.HTTP_201_CREATED)
def create_ledger_endpoint(
    payload: LedgerCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> LedgerRead:
    ledger = ledger_service.create_ledger(db, current_user, payload)
    return LedgerRead.from_orm(ledger)


@router.get("/{ledger_id}", response_model=LedgerRead)
def get_ledger(
    ledger_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> LedgerRead:
    ledger_service.ensure_membership(db, ledger_id, current_user.id)
    ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found")
    return LedgerRead.from_orm(ledger)


@router.get("/{ledger_id}/members", response_model=list[UserRead])
def list_members(
    ledger_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> list[UserRead]:
    ledger_service.ensure_membership(db, ledger_id, current_user.id)
    ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found")
    return [UserRead.from_orm(membership.user) for membership in ledger.members]


@router.post("/{ledger_id}/members/{user_id}", response_model=UserRead)
def add_member(
    ledger_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> UserRead:
    ledger_service.ensure_membership(db, ledger_id, current_user.id)
    ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found")
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    ledger_service.add_member(db, ledger, target_user)
    return UserRead.from_orm(target_user)


@router.get("/{ledger_id}/balances", response_model=list[BalanceEntry])
def get_balances_endpoint(
    ledger_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> list[BalanceEntry]:
    ledger_service.ensure_membership(db, ledger_id, current_user.id)
    return ledger_service.get_balances(db, ledger_id)
