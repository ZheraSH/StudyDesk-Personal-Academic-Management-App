"""FocusSession repository."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.database.models.focus_session import FocusSession
from src.database.repositories.base_repository import BaseRepository


class FocusSessionRepository(BaseRepository[FocusSession]):
    def __init__(self, session: Session) -> None:
        super().__init__(FocusSession, session)

    def get_by_task(self, task_id: int) -> list[FocusSession]:
        return (
            self.session.query(FocusSession)
            .options(joinedload(FocusSession.task))
            .filter(FocusSession.task_id == task_id)
            .order_by(FocusSession.started_at.desc())
            .all()
        )

    def get_in_range(self, start: datetime, end: datetime) -> list[FocusSession]:
        return (
            self.session.query(FocusSession)
            .filter(
                FocusSession.started_at >= start,
                FocusSession.started_at <= end,
                FocusSession.completed == True,
            )
            .all()
        )

    def get_total_minutes_in_range(self, start: datetime, end: datetime) -> int:
        result = (
            self.session.query(func.sum(FocusSession.duration_minutes))
            .filter(
                FocusSession.started_at >= start,
                FocusSession.started_at <= end,
                FocusSession.completed == True,
            )
            .scalar()
        )
        return result or 0

    def get_recent(self, limit: int = 10) -> list[FocusSession]:
        return (
            self.session.query(FocusSession)
            .options(joinedload(FocusSession.task))
            .order_by(FocusSession.started_at.desc())
            .limit(limit)
            .all()
        )
