"""
Tests for ScheduleService: creation, conflict detection, and weekly retrieval.
"""
from datetime import time

import pytest

from src.database.models.schedule import ScheduleType
from src.services.schedule_service import ScheduleData, ScheduleService


def test_create_schedule_success(db_session, sample_course):
    service = ScheduleService()
    data = ScheduleData(
        course_id=sample_course.id,
        day_of_week=0,  # Monday
        start_time=time(9, 0),
        end_time=time(10, 40),
        schedule_type=ScheduleType.LECTURE,
        room="Room 301",
    )
    sched, errors = service.create(data)

    assert errors == []
    assert sched is not None
    assert sched.id is not None
    assert sched.day_of_week == 0
    assert sched.start_time == time(9, 0)
    assert sched.end_time == time(10, 40)


def test_schedule_conflict_detection(db_session, sample_course):
    service = ScheduleService()
    data1 = ScheduleData(
        course_id=sample_course.id,
        day_of_week=1,  # Tuesday
        start_time=time(10, 0),
        end_time=time(11, 30),
        schedule_type=ScheduleType.LECTURE,
    )
    sched1, errors1 = service.create(data1)
    assert errors1 == []

    # Overlapping schedule on same day (10:30 to 12:00 overlaps with 10:00 to 11:30)
    data2 = ScheduleData(
        course_id=sample_course.id,
        day_of_week=1,
        start_time=time(10, 30),
        end_time=time(12, 0),
        schedule_type=ScheduleType.PRACTICUM,
    )
    sched2, errors2 = service.create(data2)
    assert sched2 is None
    assert len(errors2) > 0
    assert "conflict" in errors2[0].lower()


def test_get_weekly_schedule(db_session, sample_course):
    service = ScheduleService()
    data = ScheduleData(
        course_id=sample_course.id,
        day_of_week=2,  # Wednesday
        start_time=time(13, 0),
        end_time=time(14, 40),
        schedule_type=ScheduleType.LECTURE,
    )
    service.create(data)

    weekly = service.get_weekly()
    assert isinstance(weekly, dict)
    assert 2 in weekly
    assert len(weekly[2]) >= 1
