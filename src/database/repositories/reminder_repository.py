"""Reminder repository."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from src.database.models.reminder import Reminder
from src.database.repositories.base_repository import BaseRepository


class ReminderRepository(BaseRepository[Reminder]):
    def __init__(self, session: Session) -> None:
        super().__init__(Reminder, session)

    def get_by_task(self, task_id: int) -> list[Reminder]:
        return (
            self.session.query(Reminder)
            .options(joinedload(Reminder.task))
            .filter(Reminder.task_id == task_id)
            .order_by(Reminder.remind_at)
            .all()
        )

    def get_pending(self, now: datetime) -> list[Reminder]:
        """Reminders that are enabled, not sent, and due in the future."""
        return (
            self.session.query(Reminder)
            .options(joinedload(Reminder.task))
            .filter(
                Reminder.is_enabled == True,
                Reminder.is_sent == False,
                Reminder.remind_at > now,
            )
            .order_by(Reminder.remind_at)
            .all()
        )

    def get_due(self, now: datetime) -> list[Reminder]:
        """Reminders that are enabled, not sent, and past due time."""
        return (
            self.session.query(Reminder)
            .options(joinedload(Reminder.task))
            .filter(
                Reminder.is_enabled == True,
                Reminder.is_sent == False,
                Reminder.remind_at <= now,
            )
            .order_by(Reminder.remind_at)
            .all()
        )

    def mark_sent(self, reminder_id: int) -> None:
        reminder = self.get_by_id(reminder_id)
        if reminder:
            reminder.is_sent = True
            self.session.flush()
