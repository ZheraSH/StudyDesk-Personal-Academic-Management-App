"""Generic base repository with common CRUD operations."""
from __future__ import annotations

from typing import Any, Generic, Type, TypeVar

from sqlalchemy.orm import Session

from src.database.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Provides basic CRUD for any SQLAlchemy model."""

    def __init__(self, model: Type[ModelT], session: Session) -> None:
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> ModelT | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[ModelT]:
        return self.session.query(self.model).all()

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()

    def count(self) -> int:
        return self.session.query(self.model).count()
