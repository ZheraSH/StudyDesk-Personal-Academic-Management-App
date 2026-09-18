"""
Tests for StatisticsService: workload estimations, active counts, and weekly metrics.
"""
from datetime import timedelta

import pytest

from src.database.models.task import Priority, TaskStatus, TaskType
from src.services.statistics_service import StatisticsService
from src.services.task_service import TaskData, TaskService
from src.utils.datetime_utils import now_local


def test_task_statistics_aggregation(db_session, sample_course):
    task_service = TaskService()
    stats_service = StatisticsService()
    now = now_local()

    # 1. Create active task with 60 min estimate
    task1, _ = task_service.create(
        TaskData(
            title="Active Task 1",
            course_id=sample_course.id,
            estimated_minutes=60,
            deadline=now + timedelta(days=2),
        )
    )

    # 2. Create another active task with 45 min estimate
    task2, _ = task_service.create(
        TaskData(
            title="Active Task 2",
            course_id=sample_course.id,
            estimated_minutes=45,
            deadline=now + timedelta(days=4),
        )
    )

    # 3. Create completed task
    task3, _ = task_service.create(
        TaskData(
            title="Completed Task",
            course_id=sample_course.id,
            estimated_minutes=30,
            deadline=now + timedelta(days=1),
        )
    )
    task_service.toggle_complete(task3.id)

    stats = stats_service.get_task_stats()
    assert stats.active >= 2
    assert stats.completed >= 1
    assert stats.total_estimated_minutes >= 105  # 60 + 45


def test_weekly_statistics(db_session):
    stats_service = StatisticsService()
    weekly = stats_service.get_weekly_stats()

    assert hasattr(weekly, "tasks_completed")
    assert hasattr(weekly, "tasks_active")
    assert hasattr(weekly, "focus_minutes")
    assert hasattr(weekly, "estimated_workload_minutes")
