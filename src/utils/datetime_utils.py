"""
Datetime utilities for StudyDesk.
All datetimes are timezone-aware (Asia/Jakarta).
Never use naive datetimes internally.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from src.config.settings import TIMEZONE
from src.utils.i18n import t, get_language

ID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ID_MONTHS = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
ID_MONTHS_SHORT = [
    "", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
]


def now_local() -> datetime:
    """Return current datetime in the configured local timezone."""
    return datetime.now(TIMEZONE)


def now_utc() -> datetime:
    """Return current datetime in UTC."""
    return datetime.now(timezone.utc)


def to_local(dt: datetime) -> datetime:
    """Convert any datetime to local timezone.
    If datetime is naive (e.g. read from SQLite), assign local timezone.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TIMEZONE)
    return dt.astimezone(TIMEZONE)


def to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC.
    If datetime is naive, assume local timezone first.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TIMEZONE).astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)


def is_overdue(dt: datetime | None) -> bool:
    """Return True if the datetime is in the past (compared to now_local)."""
    if dt is None:
        return False
    return to_local(dt) < now_local()


def get_remaining(dt: datetime | None) -> timedelta | None:
    """Return timedelta remaining until deadline, or None if no deadline."""
    if dt is None:
        return None
    return to_local(dt) - now_local()


def format_remaining(dt: datetime | None) -> str:
    """Human-readable remaining time string."""
    if dt is None:
        return t("no_deadline")

    remaining = get_remaining(dt)
    assert remaining is not None

    total_seconds = int(remaining.total_seconds())

    if total_seconds < 0:
        elapsed = -total_seconds
        return t("remaining_overdue", duration=_format_duration(elapsed))

    return t("remaining_in", duration=_format_duration(total_seconds))


def format_deadline(dt: datetime | None) -> str:
    """Format deadline as a calendar-relative label."""
    if dt is None:
        return t("no_deadline")

    local_dt = to_local(dt)
    local_now = now_local()

    delta_days = (local_dt.date() - local_now.date()).days
    time_str = local_dt.strftime("%H:%M")
    lang = get_language()

    if delta_days < 0:
        if delta_days == -1:
            return t("deadline_yesterday", time=time_str)
        return t("deadline_days_ago", days=abs(delta_days))
    elif delta_days == 0:
        return t("deadline_today", time=time_str)
    elif delta_days == 1:
        return t("deadline_tomorrow", time=time_str)
    elif delta_days < 7:
        if lang == "id":
            day_name = ID_DAYS[local_dt.weekday()]
        else:
            day_name = local_dt.strftime("%A")
        return f"{day_name}, {time_str}"
    else:
        if lang == "id":
            month_name = ID_MONTHS_SHORT[local_dt.month]
            return f"{local_dt.day:02d} {month_name} {local_dt.year}, {time_str}"
        return local_dt.strftime("%d %b %Y, %H:%M")


def format_relative_short(dt: datetime | None) -> str:
    """Short relative format for list views."""
    if dt is None:
        return "—"

    local_dt = to_local(dt)
    local_now = now_local()
    delta_days = (local_dt.date() - local_now.date()).days
    lang = get_language()

    if delta_days < 0:
        return t("urgency_overdue")
    elif delta_days == 0:
        return t("urgency_today")
    elif delta_days == 1:
        return t("urgency_tomorrow")
    else:
        return f"{delta_days} hari" if lang == "id" else f"{delta_days} days"


def format_date(dt: datetime | None) -> str:
    """Format as a full date string."""
    if dt is None:
        return "—"
    local_dt = to_local(dt)
    if get_language() == "id":
        return f"{local_dt.day:02d} {ID_MONTHS[local_dt.month]} {local_dt.year}"
    return local_dt.strftime("%d %B %Y")


def format_full_header_date(dt: datetime | None = None) -> str:
    """Format full header date like 'Senin, 18 September 2026' or 'Monday, 18 September 2026'."""
    if dt is None:
        dt = now_local()
    local_dt = to_local(dt)
    if get_language() == "id":
        day_name = ID_DAYS[local_dt.weekday()]
        month_name = ID_MONTHS[local_dt.month]
        return f"{day_name}, {local_dt.day} {month_name} {local_dt.year}"
    return local_dt.strftime("%A, %d %B %Y")


def format_time(dt: datetime | None) -> str:
    """Format as a time string."""
    if dt is None:
        return "—"
    return to_local(dt).strftime("%H:%M")


def format_datetime(dt: datetime | None) -> str:
    """Format as full date + time string."""
    if dt is None:
        return "—"
    local_dt = to_local(dt)
    if get_language() == "id":
        return f"{local_dt.day:02d} {ID_MONTHS[local_dt.month]} {local_dt.year}, {local_dt.strftime('%H:%M')}"
    return local_dt.strftime("%d %B %Y, %H:%M")


def get_week_bounds(reference: datetime | None = None) -> tuple[datetime, datetime]:
    """Return (week_start, week_end) for the week containing `reference`."""
    if reference is None:
        reference = now_local()
    else:
        reference = to_local(reference)

    # Week starts on Monday
    days_since_monday = reference.weekday()
    week_start = reference.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=7) - timedelta(microseconds=1)
    return week_start, week_end


def get_urgency_level(dt: datetime | None) -> str:
    """Return urgency level string based on deadline proximity."""
    if dt is None:
        return "none"
    remaining = get_remaining(dt)
    if remaining is None:
        return "none"
    hours = remaining.total_seconds() / 3600
    if hours < 0:
        return "overdue"
    elif hours < 24:
        return "critical"
    elif hours < 72:
        return "high"
    elif hours < 168:
        return "moderate"
    else:
        return "normal"


def greeting_for_hour(hour: int | None = None) -> str:
    """Return appropriate greeting based on time of day."""
    if hour is None:
        hour = now_local().hour
    if hour < 5:
        return "Good Night"
    elif hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


def _format_duration(seconds: int) -> str:
    """Format a duration in seconds to human-readable."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    rem_minutes = minutes % 60
    if hours < 24:
        if rem_minutes:
            return f"{hours}h {rem_minutes}m"
        return f"{hours}h"
    days = hours // 24
    rem_hours = hours % 24
    if rem_hours:
        return f"{days}d {rem_hours}h"
    return f"{days}d"


def format_minutes(minutes: int | None) -> str:
    """Format estimated minutes as human-readable duration."""
    if minutes is None:
        return "—"
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    rem = minutes % 60
    if rem:
        return f"{hours}h {rem}m"
    return f"{hours}h"


def make_aware(dt: datetime, tz: ZoneInfo | None = None) -> datetime:
    """Make a naive datetime timezone-aware. Raises if already aware."""
    if dt.tzinfo is not None:
        raise ValueError(f"Datetime is already aware: {dt!r}")
    return dt.replace(tzinfo=tz or TIMEZONE)
