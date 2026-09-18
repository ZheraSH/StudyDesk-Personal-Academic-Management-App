"""
Tests for FocusService: session management and Pomodoro tracking.
"""
from datetime import timedelta
import pytest

from src.services.focus_service import FocusService
from src.utils.datetime_utils import now_local


def test_start_and_end_focus_session(db_session, sample_task):
    service = FocusService()

    # Start session
    session, err = service.start_session(task_id=sample_task.id)
    assert err == ""
    assert session is not None
    assert session.id is not None
    assert session.completed is False
    assert session.started_at is not None

    # End session
    ended, end_err = service.end_session(session.id, completed=True)
    assert end_err == ""
    assert ended is not None
    assert ended.completed is True
    assert ended.ended_at is not None
    assert ended.duration_minutes is not None
    assert ended.duration_minutes >= 1


def test_focus_minutes_aggregation(db_session):
    service = FocusService()

    # Manually create completed session with started_at in the past
    session, _ = service.start_session()
    # End session
    service.end_session(session.id, completed=True)

    today_mins = service.get_today_minutes()
    assert today_mins >= 1

    week_mins = service.get_week_minutes()
    assert week_mins >= 1


def test_get_recent_sessions(db_session, sample_task):
    service = FocusService()
    session, _ = service.start_session(sample_task.id)
    service.end_session(session.id, completed=True)

    recent = service.get_recent(limit=5)
    assert len(recent) >= 1
    assert recent[0].task_id == sample_task.id
