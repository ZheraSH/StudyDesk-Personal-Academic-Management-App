"""Focus timer service — Pomodoro session management."""
from __future__ import annotations

import logging
from datetime import datetime

from src.database.connection import get_db
from src.database.models.focus_session import FocusSession
from src.database.repositories.focus_session_repository import FocusSessionRepository
from src.utils.datetime_utils import now_local, to_local, get_week_bounds

logger = logging.getLogger(__name__)


class FocusService:
    def start_session(self, task_id: int | None = None) -> tuple[FocusSession | None, str]:
        """Start a new focus session."""
        try:
            with get_db() as session:
                fs = FocusSession(
                    task_id=task_id,
                    started_at=now_local(),
                    ended_at=None,
                    duration_minutes=None,
                    completed=False,
                )
                repo = FocusSessionRepository(session)
                repo.add(fs)
                return fs, ""
        except Exception as e:
            logger.error("Failed to start focus session: %s", e)
            return None, "Unable to start focus session. Please try again."

    def end_session(
        self,
        session_id: int,
        completed: bool = True,
    ) -> tuple[FocusSession | None, str]:
        """End a focus session, calculating duration."""
        try:
            with get_db() as session:
                repo = FocusSessionRepository(session)
                fs = repo.get_by_id(session_id)
                if not fs:
                    return None, "Focus session not found."

                ended = now_local()
                duration_seconds = (ended - to_local(fs.started_at)).total_seconds()
                duration_minutes = max(1, int(duration_seconds / 60))

                fs.ended_at = ended
                fs.duration_minutes = duration_minutes
                fs.completed = completed
                return fs, ""
        except Exception as e:
            logger.error("Failed to end focus session %d: %s", session_id, e)
            return None, "Unable to save focus session. Please try again."

    def get_today_minutes(self) -> int:
        """Total completed focus minutes today."""
        now = now_local()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            with get_db() as session:
                repo = FocusSessionRepository(session)
                return repo.get_total_minutes_in_range(day_start, now)
        except Exception as e:
            logger.error("Failed to get today focus minutes: %s", e)
            return 0

    def get_week_minutes(self) -> int:
        """Total completed focus minutes this week."""
        week_start, week_end = get_week_bounds()
        try:
            with get_db() as session:
                repo = FocusSessionRepository(session)
                return repo.get_total_minutes_in_range(week_start, week_end)
        except Exception as e:
            logger.error("Failed to get weekly focus minutes: %s", e)
            return 0

    def get_recent(self, limit: int = 10) -> list[FocusSession]:
        try:
            with get_db() as session:
                repo = FocusSessionRepository(session)
                return repo.get_recent(limit)
        except Exception as e:
            logger.error("Failed to get recent focus sessions: %s", e)
            return []
