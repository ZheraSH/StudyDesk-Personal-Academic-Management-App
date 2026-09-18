"""
Tests for ReminderService: calculation from presets, creation, and reconciliation.
"""
from datetime import datetime, timedelta

import pytest

from src.database.models.reminder import ReminderType
from src.services.reminder_service import ReminderService
from src.utils.datetime_utils import now_local


def test_calculate_remind_at():
    service = ReminderService()
    now = now_local()
    deadline = now + timedelta(days=2)

    # 1 day before
    rem_1d = service.calculate_remind_at(deadline, ReminderType.ONE_DAY)
    assert rem_1d == deadline - timedelta(days=1)

    # 3 hours before
    rem_3h = service.calculate_remind_at(deadline, ReminderType.THREE_HOURS)
    assert rem_3h == deadline - timedelta(hours=3)

    # At deadline
    rem_at = service.calculate_remind_at(deadline, ReminderType.AT_DEADLINE)
    assert rem_at == deadline

    # Custom 45 minutes before
    rem_custom = service.calculate_remind_at(deadline, ReminderType.CUSTOM, custom_minutes=45)
    assert rem_custom == deadline - timedelta(minutes=45)


def test_create_reminder_success(db_session, sample_task):
    service = ReminderService()
    deadline = sample_task.deadline

    rem, err = service.create_reminder(sample_task.id, ReminderType.ONE_HOUR, deadline)
    assert err == ""
    assert rem is not None
    assert rem.task_id == sample_task.id
    assert rem.is_sent is False
    assert rem.is_enabled is True


def test_max_reminders_limit(db_session, sample_task):
    service = ReminderService()
    deadline = sample_task.deadline

    # MAX is 5
    for _ in range(5):
        service.create_reminder(sample_task.id, ReminderType.ONE_HOUR, deadline)

    # 6th should fail
    rem6, err = service.create_reminder(sample_task.id, ReminderType.ONE_HOUR, deadline)
    assert rem6 is None
    assert "Maximum" in err


def test_reconcile_on_startup(db_session, sample_task):
    service = ReminderService()
    # Create a reminder whose remind_at was 2 hours ago
    past_deadline = now_local() - timedelta(hours=1)
    rem, _ = service.create_reminder(sample_task.id, ReminderType.ONE_HOUR, past_deadline)

    assert rem is not None
    # Run startup reconciliation
    missed_count = service.reconcile_on_startup()
    assert missed_count >= 1
