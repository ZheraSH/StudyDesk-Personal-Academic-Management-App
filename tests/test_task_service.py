"""
Tests for TaskService business logic: CRUD, filtering, validation, and completion.
"""
from datetime import datetime, timedelta

import pytest

from src.config.settings import TIMEZONE
from src.database.models.task import Priority, TaskStatus, TaskType
from src.services.task_service import TaskData, TaskService
from src.utils.datetime_utils import now_local


def test_create_task_success(db_session, sample_course):
    service = TaskService()
    now = now_local()
    data = TaskData(
        title="Distributed Systems Lab 1",
        course_id=sample_course.id,
        task_type=TaskType.ASSIGNMENT,
        priority=Priority.HIGH,
        status=TaskStatus.INBOX,
        deadline=now + timedelta(days=3),
        estimated_minutes=90,
    )
    task, errors = service.create(data)

    assert errors == []
    assert task is not None
    assert task.id is not None
    assert task.title == "Distributed Systems Lab 1"
    assert task.status == TaskStatus.INBOX
    assert task.priority == Priority.HIGH


def test_create_task_validation_error_empty_title(db_session):
    service = TaskService()
    data = TaskData(title="   ")
    task, errors = service.create(data)

    assert task is None
    assert len(errors) > 0
    assert any("title" in err.lower() or "empty" in err.lower() for err in errors)


def test_toggle_complete_task(db_session, sample_task):
    service = TaskService()
    assert sample_task.status != TaskStatus.COMPLETED

    # Toggle to complete
    updated, msg = service.toggle_complete(sample_task.id)
    assert updated is not None
    assert updated.status == TaskStatus.COMPLETED
    assert updated.completed_at is not None

    # Toggle back to in progress
    updated2, msg2 = service.toggle_complete(sample_task.id)
    assert updated2 is not None
    assert updated2.status == TaskStatus.IN_PROGRESS
    assert updated2.completed_at is None


def test_get_overdue_and_urgent(db_session, sample_course):
    service = TaskService()
    now = now_local()

    # Create overdue task
    past_data = TaskData(
        title="Past Overdue Task",
        course_id=sample_course.id,
        deadline=now - timedelta(days=1),
        is_reschedule=True,
    )
    overdue_task, _ = service.create(past_data)

    # Create urgent task (due in 5 hours)
    urgent_data = TaskData(
        title="Urgent Task Today",
        course_id=sample_course.id,
        deadline=now + timedelta(hours=5),
    )
    urgent_task, _ = service.create(urgent_data)

    overdue_list = service.get_overdue()
    assert any(t.id == overdue_task.id for t in overdue_list)

    urgent_list = service.get_urgent(within_hours=24)
    assert any(t.id == urgent_task.id for t in urgent_list)


def test_delete_task(db_session, sample_task):
    service = TaskService()
    success, msg = service.delete(sample_task.id)
    assert success is True

    fetched = service.get_by_id(sample_task.id)
    assert fetched is None
