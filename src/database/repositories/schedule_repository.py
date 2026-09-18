"""Schedule repository."""
from __future__ import annotations

from datetime import time

from sqlalchemy.orm import Session, joinedload

from src.database.models.schedule import Schedule, ScheduleType
from src.database.repositories.base_repository import BaseRepository


class ScheduleRepository(BaseRepository[Schedule]):
    def __init__(self, session: Session) -> None:
        super().__init__(Schedule, session)

    def get_all_active(self) -> list[Schedule]:
        return (
            self.session.query(Schedule)
            .options(joinedload(Schedule.course))
            .filter(Schedule.is_active == True)
            .order_by(Schedule.day_of_week, Schedule.start_time)
            .all()
        )

    def get_by_day(self, day_of_week: int) -> list[Schedule]:
        return (
            self.session.query(Schedule)
            .options(joinedload(Schedule.course))
            .filter(Schedule.day_of_week == day_of_week, Schedule.is_active == True)
            .order_by(Schedule.start_time)
            .all()
        )

    def get_weekly(self) -> dict[int, list[Schedule]]:
        """Return all active schedules grouped by day_of_week (0=Mon..6=Sun)."""
        all_schedules = self.get_all_active()
        result: dict[int, list[Schedule]] = {i: [] for i in range(7)}
        for s in all_schedules:
            result[s.day_of_week].append(s)
        return result

    def check_conflict(
        self,
        day_of_week: int,
        start_time: time,
        end_time: time,
        exclude_id: int | None = None,
    ) -> list[Schedule]:
        """Return schedules that overlap with the given time range on a day."""
        query = (
            self.session.query(Schedule)
            .filter(
                Schedule.day_of_week == day_of_week,
                Schedule.is_active == True,
                Schedule.start_time < end_time,
                Schedule.end_time > start_time,
            )
        )
        if exclude_id is not None:
            query = query.filter(Schedule.id != exclude_id)
        return query.all()

    def get_by_course(self, course_id: int) -> list[Schedule]:
        return (
            self.session.query(Schedule)
            .filter(Schedule.course_id == course_id)
            .order_by(Schedule.day_of_week, Schedule.start_time)
            .all()
        )
