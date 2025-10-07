from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

from app.infrastructure.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, obj_id):
        return db.query(self.model).get(obj_id)

    def list(self, db: Session):
        return db.query(self.model).all()
