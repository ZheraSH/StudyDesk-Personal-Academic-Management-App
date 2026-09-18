"""Schedule service — business logic for weekly schedule management."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import time

from sqlalchemy.orm import joinedload

from src.database.connection import get_db
from src.database.models.schedule import DayOfWeek, Schedule, ScheduleType
from src.database.repositories.schedule_repository import ScheduleRepository
from src.utils.datetime_utils import now_local
from src.utils.validation import validate_schedule

logger = logging.getLogger(__name__)


@dataclass
class ScheduleData:
    course_id: int
    day_of_week: int
    start_time: time
    end_time: time
    schedule_type: ScheduleType = ScheduleType.LECTURE
    room: str = ""
    notes: str = ""
    is_active: bool = True


class ScheduleService:
    def get_all(self) -> list[Schedule]:
        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                return repo.get_all_active()
        except Exception as e:
            logger.error("Failed to get schedules: %s", e)
            return []

    def get_weekly(self) -> dict[int, list[Schedule]]:
        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                return repo.get_weekly()
        except Exception as e:
            logger.error("Failed to get weekly schedules: %s", e)
            return {i: [] for i in range(7)}

    def get_today(self) -> list[Schedule]:
        """Return today's schedules in time order."""
        today_dow = now_local().weekday()  # 0=Monday
        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                return repo.get_by_day(today_dow)
        except Exception as e:
            logger.error("Failed to get today's schedules: %s", e)
            return []

    def get_next_class(self) -> Schedule | None:
        """Return the next upcoming class/practical from now."""
        now = now_local()
        current_dow = now.weekday()
        current_time = now.time()

        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                weekly = repo.get_weekly()

            # First: check rest of today
            today_schedules = weekly.get(current_dow, [])
            for s in today_schedules:
                if s.start_time > current_time:
                    return s

            # Then: check next 6 days
            for offset in range(1, 7):
                next_dow = (current_dow + offset) % 7
                day_schedules = weekly.get(next_dow, [])
                if day_schedules:
                    return day_schedules[0]

            return None
        except Exception as e:
            logger.error("Failed to get next class: %s", e)
            return None

    def create(self, data: ScheduleData) -> tuple[Schedule | None, list[str]]:
        errors = validate_schedule({
            "course_id": data.course_id,
            "day_of_week": data.day_of_week,
            "start_time": data.start_time,
            "end_time": data.end_time,
        })
        if errors:
            return None, errors

        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                conflicts = repo.check_conflict(data.day_of_week, data.start_time, data.end_time)
                if conflicts:
                    return None, [
                        f"Schedule conflict with existing class on "
                        f"{DayOfWeek(data.day_of_week).display_name} "
                        f"({conflicts[0].start_time.strftime('%H:%M')}–{conflicts[0].end_time.strftime('%H:%M')})."
                    ]

                schedule = Schedule(
                    course_id=data.course_id,
                    day_of_week=data.day_of_week,
                    start_time=data.start_time,
                    end_time=data.end_time,
                    schedule_type=data.schedule_type,
                    room=(data.room or "").strip() or None,
                    notes=(data.notes or "").strip() or None,
                    is_active=data.is_active,
                )
                repo.add(schedule)
                saved = (
                    session.query(Schedule)
                    .options(joinedload(Schedule.course))
                    .filter(Schedule.id == schedule.id)
                    .first()
                )
                return saved or schedule, []
        except Exception as e:
            logger.error("Failed to create schedule: %s", e)
            return None, ["Unable to save schedule. Please try again."]

    def update(self, schedule_id: int, data: ScheduleData) -> tuple[Schedule | None, list[str]]:
        errors = validate_schedule({
            "course_id": data.course_id,
            "day_of_week": data.day_of_week,
            "start_time": data.start_time,
            "end_time": data.end_time,
        })
        if errors:
            return None, errors

        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                schedule = repo.get_by_id(schedule_id)
                if not schedule:
                    return None, ["Schedule not found."]

                conflicts = repo.check_conflict(
                    data.day_of_week, data.start_time, data.end_time, exclude_id=schedule_id
                )
                if conflicts:
                    return None, [
                        f"Schedule conflict with existing class on "
                        f"{DayOfWeek(data.day_of_week).display_name}."
                    ]

                schedule.course_id = data.course_id
                schedule.day_of_week = data.day_of_week
                schedule.start_time = data.start_time
                schedule.end_time = data.end_time
                schedule.schedule_type = data.schedule_type
                schedule.room = (data.room or "").strip() or None
                schedule.notes = (data.notes or "").strip() or None
                schedule.is_active = data.is_active
                saved = (
                    session.query(Schedule)
                    .options(joinedload(Schedule.course))
                    .filter(Schedule.id == schedule.id)
                    .first()
                )
                return saved or schedule, []
        except Exception as e:
            logger.error("Failed to update schedule %d: %s", schedule_id, e)
            return None, ["Unable to update schedule. Please try again."]

    def delete(self, schedule_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = ScheduleRepository(session)
                schedule = repo.get_by_id(schedule_id)
                if not schedule:
                    return False, "Schedule not found."
                repo.delete(schedule)
                return True, ""
        except Exception as e:
            logger.error("Failed to delete schedule %d: %s", schedule_id, e)
            return False, "Unable to delete schedule. Please try again."
