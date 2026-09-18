"""Statistics service — aggregated academic metrics."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from src.database.connection import get_db
from src.database.models.task import TaskStatus
from src.database.repositories.task_repository import TaskRepository
from src.services.focus_service import FocusService
from src.utils.datetime_utils import now_local, get_week_bounds

logger = logging.getLogger(__name__)


@dataclass
class TaskStats:
    active: int
    completed: int
    overdue: int
    completed_this_week: int
    total_estimated_minutes: int  # For active tasks


@dataclass
class WeeklyStats:
    tasks_completed: int
    tasks_active: int
    tasks_overdue: int
    focus_minutes: int
    estimated_workload_minutes: int


class StatisticsService:
    def __init__(self) -> None:
        self._focus_service = FocusService()

    def get_task_stats(self) -> TaskStats:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                now = now_local()

                active = repo.get_all_active()
                overdue = repo.get_overdue(now)
                week_start, week_end = get_week_bounds(now)
                completed_week = repo.get_completed_this_week(week_start, week_end)

                # Count all completed (not just this week)
                all_tasks = repo.get_filtered(include_completed=True, include_archived=False)
                completed_all = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]

                total_est = sum(
                    (t.estimated_minutes or 0)
                    for t in active
                    if t.status not in (TaskStatus.COMPLETED, TaskStatus.ARCHIVED)
                )

                return TaskStats(
                    active=len(active),
                    completed=len(completed_all),
                    overdue=len(overdue),
                    completed_this_week=len(completed_week),
                    total_estimated_minutes=total_est,
                )
        except Exception as e:
            logger.error("Failed to get task stats: %s", e)
            return TaskStats(0, 0, 0, 0, 0)

    def get_weekly_stats(self) -> WeeklyStats:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                now = now_local()
                week_start, week_end = get_week_bounds(now)

                completed_week = repo.get_completed_this_week(week_start, week_end)
                active = repo.get_all_active()
                overdue = repo.get_overdue(now)

                total_est = sum(
                    (t.estimated_minutes or 0) for t in active
                )

            focus_minutes = self._focus_service.get_week_minutes()

            return WeeklyStats(
                tasks_completed=len(completed_week),
                tasks_active=len(active),
                tasks_overdue=len(overdue),
                focus_minutes=focus_minutes,
                estimated_workload_minutes=total_est,
            )
        except Exception as e:
            logger.error("Failed to get weekly stats: %s", e)
            return WeeklyStats(0, 0, 0, 0, 0)
