from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain import models
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.utils import security


def create_user(db: Session, user_in: UserCreate) -> models.User:
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        timezone=user_in.timezone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ledger = models.Ledger(name=f"{user.full_name or user.email}'s Ledger", owner=user)
    db.add(ledger)
    db.flush()
    membership = models.LedgerMembership(ledger=ledger, user=user, role="owner")
    db.add(membership)
    db.commit()
    return user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user


def create_tokens_for_user(user: models.User) -> Token:
    access = security.create_access_token({"sub": user.email})
    refresh = security.create_refresh_token({"sub": user.email})
    return Token(access_token=access, refresh_token=refresh)
