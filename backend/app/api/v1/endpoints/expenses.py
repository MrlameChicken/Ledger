import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.domain import models
from app.domain.services import expense_service
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(
    ledger_id: uuid.UUID | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> list[ExpenseRead]:
    expenses = expense_service.list_expenses(db, ledger_id, current_user)
    return [ExpenseRead.from_orm(expense) for expense in expenses]


@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(
    payload: ExpenseCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ExpenseRead:
    expense = expense_service.create_expense(db, current_user, payload)
    return ExpenseRead.from_orm(expense)


@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense_endpoint(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ExpenseRead:
    expense = expense_service.update_expense(db, expense_id, current_user, payload)
    return ExpenseRead.from_orm(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> None:
    expense_service.delete_expense(db, expense_id, current_user)
