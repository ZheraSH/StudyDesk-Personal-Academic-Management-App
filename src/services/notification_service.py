"""
Notification service — bridges ReminderService and platform adapters.
UI calls this service; never calls adapters directly.
"""
from __future__ import annotations

import logging
from typing import Callable

from src.notifications.adapter_factory import get_adapter
from src.database.models.reminder import Reminder
from src.database.models.task import Task

logger = logging.getLogger(__name__)


class NotificationService:
    """Orchestrates reminder-to-notification delivery."""

    def __init__(self, on_in_app_notification: Callable[[str, str], None] | None = None) -> None:
        """
        Args:
            on_in_app_notification: Optional callback for in-app notification display.
                Called as on_in_app_notification(title, body) when app is open.
        """
        self._adapter = get_adapter()
        self._on_in_app = on_in_app_notification

    def schedule_reminder(self, reminder: Reminder, task: Task) -> bool:
        """Schedule a platform notification for a reminder."""
        title = f"StudyDesk — {task.title}"
        body = self._build_reminder_body(reminder, task)
        data = {"task_id": task.id, "reminder_id": reminder.id}

        success = self._adapter.schedule(
            notification_id=reminder.id,
            remind_at=reminder.remind_at,
            title=title,
            body=body,
            data=data,
        )

        if not success and not self._adapter.is_available():
            logger.warning("Notification adapter unavailable for reminder %d.", reminder.id)

        return success

    def send_now(self, reminder: Reminder, task: Task) -> bool:
        """Send an immediate notification (for missed/due reminders)."""
        title = f"StudyDesk — {task.title}"
        body = self._build_reminder_body(reminder, task)

        # Trigger in-app callback if registered
        if self._on_in_app:
            try:
                self._on_in_app(title, body)
            except Exception as e:
                logger.warning("In-app notification callback failed: %s", e)

        return self._adapter.send_now(
            notification_id=reminder.id,
            title=title,
            body=body,
            data={"task_id": task.id, "reminder_id": reminder.id},
        )

    def cancel_reminder(self, reminder_id: int) -> None:
        self._adapter.cancel(reminder_id)

    def cancel_all(self) -> None:
        self._adapter.cancel_all()

    @staticmethod
    def _build_reminder_body(reminder: Reminder, task: Task) -> str:
        from src.utils.datetime_utils import format_deadline
        deadline_str = format_deadline(task.deadline) if task.deadline else "No deadline"
        course_str = f" ({task.course.name})" if task.course else ""
        estimated_str = (
            f" · Est. {task.estimated_minutes} min" if task.estimated_minutes else ""
        )
        return f"{task.title}{course_str}\nDeadline: {deadline_str}{estimated_str}"

    def reschedule_all_pending(self) -> None:
        """Reschedule all pending reminders from DB. Call after app restart."""
        from src.services.reminder_service import ReminderService
        reminder_service = ReminderService()
        pending = reminder_service.get_pending()

        scheduled = 0
        for reminder in pending:
            if reminder.task:
                success = self.schedule_reminder(reminder, reminder.task)
                if success:
                    scheduled += 1

        logger.info("Rescheduled %d/%d pending reminders.", scheduled, len(pending))
