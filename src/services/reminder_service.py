"""Reminder service — reminder calculation, scheduling, and reconciliation."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from src.config.settings import REMINDER_PRESETS, MAX_REMINDERS_PER_TASK
from src.database.connection import get_db
from src.database.models.reminder import Reminder, ReminderType
from src.database.repositories.reminder_repository import ReminderRepository
from src.utils.datetime_utils import now_local, to_local

logger = logging.getLogger(__name__)


class ReminderService:
    def get_by_task(self, task_id: int) -> list[Reminder]:
        try:
            with get_db() as session:
                repo = ReminderRepository(session)
                return repo.get_by_task(task_id)
        except Exception as e:
            logger.error("Failed to get reminders for task %d: %s", task_id, e)
            return []

    def create_reminder(
        self,
        task_id: int,
        reminder_type: ReminderType,
        deadline: datetime,
        custom_minutes_before: int | None = None,
    ) -> tuple[Reminder | None, str]:
        """Create a reminder for a task, calculated from the deadline."""
        try:
            with get_db() as session:
                repo = ReminderRepository(session)

                # Enforce limit
                existing = repo.get_by_task(task_id)
                if len(existing) >= MAX_REMINDERS_PER_TASK:
                    return None, f"Maximum {MAX_REMINDERS_PER_TASK} reminders per task."

                remind_at = self.calculate_remind_at(deadline, reminder_type, custom_minutes_before)
                if remind_at is None:
                    return None, "Unable to calculate reminder time."

                reminder = Reminder(
                    task_id=task_id,
                    remind_at=remind_at,
                    reminder_type=reminder_type,
                    is_enabled=True,
                    is_sent=False,
                    minutes_before=custom_minutes_before,
                )
                repo.add(reminder)
                return reminder, ""
        except Exception as e:
            logger.error("Failed to create reminder for task %d: %s", task_id, e)
            return None, "Unable to save reminder. Please try again."

    def calculate_remind_at(
        self,
        deadline: datetime,
        reminder_type: ReminderType,
        custom_minutes: int | None = None,
    ) -> datetime | None:
        """Calculate the absolute remind_at datetime from a deadline and preset."""
        preset_map = {
            ReminderType.THREE_DAYS: 3 * 24 * 60,
            ReminderType.ONE_DAY: 24 * 60,
            ReminderType.TWELVE_HOURS: 12 * 60,
            ReminderType.THREE_HOURS: 3 * 60,
            ReminderType.ONE_HOUR: 60,
            ReminderType.THIRTY_MINUTES: 30,
            ReminderType.AT_DEADLINE: 0,
            ReminderType.CUSTOM: custom_minutes,
        }
        minutes = preset_map.get(reminder_type)
        if minutes is None:
            return None
        return to_local(deadline) - timedelta(minutes=minutes)

    def delete_reminder(self, reminder_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = ReminderRepository(session)
                reminder = repo.get_by_id(reminder_id)
                if not reminder:
                    return False, "Reminder not found."
                repo.delete(reminder)
                return True, ""
        except Exception as e:
            logger.error("Failed to delete reminder %d: %s", reminder_id, e)
            return False, "Unable to delete reminder. Please try again."

    def get_pending(self) -> list[Reminder]:
        """Reminders that are enabled, not sent, due in the future."""
        try:
            with get_db() as session:
                repo = ReminderRepository(session)
                return repo.get_pending(now_local())
        except Exception as e:
            logger.error("Failed to get pending reminders: %s", e)
            return []

    def get_due_now(self) -> list[Reminder]:
        """Reminders that are past due but not yet sent."""
        try:
            with get_db() as session:
                repo = ReminderRepository(session)
                return repo.get_due(now_local())
        except Exception as e:
            logger.error("Failed to get due reminders: %s", e)
            return []

    def mark_sent(self, reminder_id: int) -> None:
        try:
            with get_db() as session:
                repo = ReminderRepository(session)
                repo.mark_sent(reminder_id)
        except Exception as e:
            logger.error("Failed to mark reminder %d as sent: %s", reminder_id, e)

    def reconcile_on_startup(self) -> int:
        """
        On app startup:
        1. Find reminders that are past due and not sent.
        2. Mark them as sent (they were missed while app was closed).
        3. Return count of reconciled reminders.

        This prevents showing stale notifications for past reminders.
        """
        try:
            missed_count = 0
            with get_db() as session:
                repo = ReminderRepository(session)
                missed = repo.get_due(now_local())
                for reminder in missed:
                    reminder.is_sent = True
                    missed_count += 1
                if missed_count:
                    logger.info("Reconciled %d missed reminders on startup.", missed_count)
            return missed_count
        except Exception as e:
            logger.error("Failed to reconcile reminders: %s", e)
            return 0

    def reschedule_reminders_for_task(self, task_id: int, new_deadline: datetime) -> None:
        """When a task deadline changes, recalculate all reminder times."""
        try:
            with get_db() as session:
                repo = ReminderRepository(session)
                reminders = repo.get_by_task(task_id)
                for reminder in reminders:
                    new_remind_at = self.calculate_remind_at(
                        new_deadline, reminder.reminder_type, reminder.minutes_before
                    )
                    if new_remind_at:
                        reminder.remind_at = new_remind_at
                        reminder.is_sent = False  # Re-enable
        except Exception as e:
            logger.error("Failed to reschedule reminders for task %d: %s", task_id, e)
