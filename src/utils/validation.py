"""
Validation utilities for StudyDesk.
Returns lists of user-friendly error messages.
"""
from __future__ import annotations

from datetime import datetime, time
from typing import Any

from src.utils.datetime_utils import now_local, to_local


# ─────────────────────────── Task Validation ─────────────────────────

def validate_task(data: dict[str, Any], is_reschedule: bool = False) -> list[str]:
    """Validate task creation/update data.

    Returns a list of error strings (empty = valid).
    """
    errors: list[str] = []

    title = (data.get("title") or "").strip()
    if not title:
        errors.append("Task title is required.")
    elif len(title) > 500:
        errors.append("Task title must be 500 characters or fewer.")

    deadline = data.get("deadline")
    if deadline is not None:
        if isinstance(deadline, datetime):
            local_deadline = to_local(deadline)
            if not is_reschedule and local_deadline < now_local():
                errors.append(
                    "Deadline cannot be in the past. "
                    "If rescheduling an overdue task, use the Reschedule option."
                )
        else:
            errors.append("Deadline must be a datetime object.")

    estimated = data.get("estimated_minutes")
    if estimated is not None:
        if not isinstance(estimated, int) or estimated <= 0:
            errors.append("Estimated duration must be a positive number of minutes.")
        elif estimated > 60 * 24 * 7:
            errors.append("Estimated duration seems unreasonably large (max 1 week = 10080 min).")

    planned_start = data.get("planned_start")
    planned_end = data.get("planned_end")
    if planned_start is not None and planned_end is not None:
        if isinstance(planned_start, datetime) and isinstance(planned_end, datetime):
            if to_local(planned_start) >= to_local(planned_end):
                errors.append("Planned start must be before planned end.")
        else:
            errors.append("Planned start and end must be datetime objects.")

    return errors


# ─────────────────────────── Schedule Validation ─────────────────────

def validate_schedule(data: dict[str, Any]) -> list[str]:
    """Validate schedule creation/update data."""
    errors: list[str] = []

    course_id = data.get("course_id")
    if not course_id:
        errors.append("A course must be selected.")

    day = data.get("day_of_week")
    if day is None or not isinstance(day, int) or not (0 <= day <= 6):
        errors.append("A valid day of the week must be selected.")

    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if start_time is None:
        errors.append("Start time is required.")
    if end_time is None:
        errors.append("End time is required.")

    if start_time is not None and end_time is not None:
        if isinstance(start_time, time) and isinstance(end_time, time):
            if start_time >= end_time:
                errors.append("Start time must be before end time.")
        else:
            errors.append("Start and end time must be time objects.")

    return errors


# ─────────────────────────── Reminder Validation ─────────────────────

def validate_reminder(data: dict[str, Any]) -> list[str]:
    """Validate reminder data."""
    errors: list[str] = []

    task_id = data.get("task_id")
    if not task_id:
        errors.append("A task must be linked to the reminder.")

    remind_at = data.get("remind_at")
    if remind_at is None:
        errors.append("Reminder time is required.")
    elif isinstance(remind_at, datetime):
        pass  # Time can be in the past only for already-sent reminders
    else:
        errors.append("Reminder time must be a datetime object.")

    return errors


# ─────────────────────────── Course Validation ───────────────────────

def validate_course(data: dict[str, Any]) -> list[str]:
    """Validate course creation/update data."""
    errors: list[str] = []

    name = (data.get("name") or "").strip()
    if not name:
        errors.append("Course name is required.")
    elif len(name) > 200:
        errors.append("Course name must be 200 characters or fewer.")

    code = data.get("code") or ""
    if code and len(code) > 20:
        errors.append("Course code must be 20 characters or fewer.")

    color = data.get("color") or ""
    if color and (not color.startswith("#") or len(color) not in (4, 7)):
        errors.append("Course color must be a valid hex color (e.g. #6F5A8E).")

    return errors


# ─────────────────────────── Semester Validation ─────────────────────

def validate_semester(data: dict[str, Any]) -> list[str]:
    """Validate semester creation/update data."""
    errors: list[str] = []

    name = (data.get("name") or "").strip()
    if not name:
        errors.append("Semester name is required.")
    elif len(name) > 100:
        errors.append("Semester name must be 100 characters or fewer.")

    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if start_date and end_date:
        if start_date >= end_date:
            errors.append("Semester start date must be before end date.")

    return errors
