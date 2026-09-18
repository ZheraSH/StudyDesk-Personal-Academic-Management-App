"""Reminder model — scheduled notifications for a Task."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class ReminderType(str, enum.Enum):
    THREE_DAYS = "3 days before"
    ONE_DAY = "1 day before"
    TWELVE_HOURS = "12 hours before"
    THREE_HOURS = "3 hours before"
    ONE_HOUR = "1 hour before"
    THIRTY_MINUTES = "30 minutes before"
    AT_DEADLINE = "At deadline"
    CUSTOM = "Custom"


class Reminder(Base, TimestampMixin):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reminder_type: Mapped[ReminderType] = mapped_column(
        Enum(ReminderType), nullable=False, default=ReminderType.ONE_DAY
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Minutes before deadline (for custom type reference)
    minutes_before: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    task: Mapped["Task"] = relationship(  # type: ignore[name-defined]
        "Task", back_populates="reminders", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<Reminder id={self.id} task_id={self.task_id} "
            f"at={self.remind_at} sent={self.is_sent}>"
        )
