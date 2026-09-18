"""
Windows notification adapter.
Uses plyer for toast notifications.
Scheduled notifications use a background thread with sched.
"""
from __future__ import annotations

import logging
import sched
import threading
import time as time_module
from datetime import datetime

from src.notifications.base_adapter import NotificationAdapter
from src.utils.datetime_utils import now_local

logger = logging.getLogger(__name__)


class WindowsNotificationAdapter(NotificationAdapter):
    """Delivers Windows toast notifications via plyer."""

    def __init__(self) -> None:
        self._scheduler = sched.scheduler(time_module.monotonic, time_module.sleep)
        self._scheduled_events: dict[int, sched.Event] = {}
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._running = False

    @property
    def platform_name(self) -> str:
        return "Windows"

    def is_available(self) -> bool:
        try:
            from plyer import notification  # noqa: F401
            return True
        except ImportError:
            return False

    def send_now(self, notification_id: int, title: str, body: str, data: dict | None = None) -> bool:
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=body,
                app_name="StudyDesk",
                timeout=10,
            )
            return True
        except Exception as e:
            logger.warning("Failed to send Windows notification: %s", e)
            return False

    def schedule(self, notification_id: int, remind_at: datetime, title: str, body: str, data: dict | None = None) -> bool:
        now = now_local()
        delay_seconds = (remind_at - now).total_seconds()

        if delay_seconds <= 0:
            # Already past — send immediately
            return self.send_now(notification_id, title, body, data)

        try:
            with self._lock:
                # Cancel existing if rescheduling same ID
                if notification_id in self._scheduled_events:
                    try:
                        self._scheduler.cancel(self._scheduled_events[notification_id])
                    except ValueError:
                        pass  # Already fired

                event = self._scheduler.enter(
                    delay=delay_seconds,
                    priority=1,
                    action=self._fire_notification,
                    argument=(notification_id, title, body, data),
                )
                self._scheduled_events[notification_id] = event

            self._ensure_thread_running()
            logger.info("Scheduled notification %d for %s (in %.0fs)", notification_id, remind_at, delay_seconds)
            return True
        except Exception as e:
            logger.error("Failed to schedule notification %d: %s", notification_id, e)
            return False

    def cancel(self, notification_id: int) -> bool:
        with self._lock:
            if notification_id in self._scheduled_events:
                try:
                    self._scheduler.cancel(self._scheduled_events.pop(notification_id))
                    return True
                except ValueError:
                    self._scheduled_events.pop(notification_id, None)
        return False

    def cancel_all(self) -> None:
        with self._lock:
            for event in list(self._scheduled_events.values()):
                try:
                    self._scheduler.cancel(event)
                except ValueError:
                    pass
            self._scheduled_events.clear()

    def _fire_notification(self, notification_id: int, title: str, body: str, data: dict | None) -> None:
        with self._lock:
            self._scheduled_events.pop(notification_id, None)
        self.send_now(notification_id, title, body, data)

    def _ensure_thread_running(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self._running = True
            self._thread = threading.Thread(
                target=self._run_scheduler,
                daemon=True,
                name="StudyDesk-NotificationThread",
            )
            self._thread.start()

    def _run_scheduler(self) -> None:
        """Run the scheduler in a loop until there are no more events."""
        while self._running:
            with self._lock:
                next_event = self._scheduler.queue[0] if self._scheduler.queue else None

            if next_event is None:
                break

            self._scheduler.run(blocking=False)
            time_module.sleep(5)  # Check every 5 seconds
