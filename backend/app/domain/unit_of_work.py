from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.infrastructure.db import SessionLocal


class UnitOfWork(AbstractContextManager[Session]):
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> Session:
        self.session = self._session_factory()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        assert self.session is not None
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
