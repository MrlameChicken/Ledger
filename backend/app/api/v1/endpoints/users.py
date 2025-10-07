from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.domain import models
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> UserRead:
    return UserRead.from_orm(current_user)


@router.put("/me", response_model=UserRead)
def update_current_user(
    payload: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> UserRead:
    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserRead.from_orm(current_user)
