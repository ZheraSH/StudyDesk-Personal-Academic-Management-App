"""
Tests for datetime utilities and timezone handling.
Ensures datetimes are always timezone-aware and formatting is accurate.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from src.config.settings import TIMEZONE
from src.utils.datetime_utils import (
    now_local,
    now_utc,
    to_local,
    to_utc,
    is_overdue,
    get_remaining,
    format_remaining,
    format_deadline,
    get_urgency_level,
    get_week_bounds,
)


def test_now_local_is_aware_and_correct_tz():
    now = now_local()
    assert now.tzinfo is not None
    # Offset should be UTC+7 (+25200 seconds)
    offset = now.utcoffset()
    assert offset == timedelta(hours=7)


def test_now_utc_is_aware():
    utc = now_utc()
    assert utc.tzinfo is not None
    assert utc.utcoffset() == timedelta(0)


def test_to_local_converts_correctly():
    utc_dt = datetime(2026, 9, 18, 5, 0, 0, tzinfo=timezone.utc)
    local_dt = to_local(utc_dt)
    assert local_dt.hour == 12  # UTC+7
    assert local_dt.minute == 0


def test_to_local_handles_naive_datetime():
    naive_dt = datetime(2026, 9, 18, 12, 0, 0)
    local_dt = to_local(naive_dt)
    assert local_dt.tzinfo is not None
    assert local_dt.utcoffset() == timedelta(hours=7)
    assert local_dt.hour == 12


def test_is_overdue_logic():
    now = now_local()
    past = now - timedelta(hours=2)
    future = now + timedelta(hours=2)

    assert is_overdue(past) is True
    assert is_overdue(future) is False
    assert is_overdue(None) is False


def test_format_remaining():
    now = now_local()
    future = now + timedelta(days=2, hours=3)
    past = now - timedelta(hours=1, minutes=30)

    rem_str = format_remaining(future)
    assert "In" in rem_str or "Dalam" in rem_str
    assert "2d" in rem_str

    overdue_str = format_remaining(past)
    assert "Overdue" in overdue_str or "Terlambat" in overdue_str
    assert "1h" in overdue_str


def test_urgency_levels():
    now = now_local()
    assert get_urgency_level(now - timedelta(hours=1)) == "overdue"
    assert get_urgency_level(now + timedelta(hours=12)) == "critical"  # <= 24h
    assert get_urgency_level(now + timedelta(days=2)) == "high"        # <= 3 days
    assert get_urgency_level(now + timedelta(days=5)) == "moderate"    # <= 7 days
    assert get_urgency_level(now + timedelta(days=10)) == "normal"     # > 7 days
    assert get_urgency_level(None) == "none"


def test_week_bounds():
    now = now_local()
    start, end = get_week_bounds(now)
    assert start.weekday() == 0  # Monday
    assert start.hour == 0 and start.minute == 0 and start.second == 0
    assert end.hour == 23 and end.minute == 59 and end.second == 59
    assert end > start
