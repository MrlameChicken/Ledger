import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.domain import models
from app.domain.services import settlement_service
from app.schemas.settlement import SettlementCreate, SettlementRead

router = APIRouter(prefix="/settlements", tags=["settlements"])


@router.get("/", response_model=list[SettlementRead])
def list_settlements(
    ledger_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> list[SettlementRead]:
    settlements = settlement_service.list_settlements(db, ledger_id, current_user)
    return [SettlementRead.from_orm(item) for item in settlements]


@router.post("/", response_model=SettlementRead, status_code=status.HTTP_201_CREATED)
def create_settlement_endpoint(
    payload: SettlementCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> SettlementRead:
    settlement = settlement_service.create_settlement(db, current_user, payload)
    return SettlementRead.from_orm(settlement)


@router.post("/{settlement_id}/confirm", response_model=SettlementRead)
def confirm_settlement_endpoint(
    settlement_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> SettlementRead:
    settlement = settlement_service.confirm_settlement(db, settlement_id, current_user)
    return SettlementRead.from_orm(settlement)
