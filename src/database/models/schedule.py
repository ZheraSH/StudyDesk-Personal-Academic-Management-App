"""Schedule model — recurring weekly class/practicum entries."""
from __future__ import annotations

import enum
from datetime import time

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class ScheduleType(str, enum.Enum):
    LECTURE = "Lecture"
    PRACTICUM = "Practicum"
    OTHER = "Other"


class DayOfWeek(int, enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @property
    def display_name(self) -> str:
        return self.name.capitalize()

    @property
    def short_name(self) -> str:
        return self.name[:3].upper()


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    schedule_type: Mapped[ScheduleType] = mapped_column(
        Enum(ScheduleType), nullable=False, default=ScheduleType.LECTURE
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon..6=Sun
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship(  # type: ignore[name-defined]
        "Course", back_populates="schedules", lazy="joined"
    )

    @property
    def day_name(self) -> str:
        return DayOfWeek(self.day_of_week).display_name

    def __repr__(self) -> str:
        return (
            f"<Schedule id={self.id} course_id={self.course_id} "
            f"day={self.day_of_week} {self.start_time}-{self.end_time}>"
        )
