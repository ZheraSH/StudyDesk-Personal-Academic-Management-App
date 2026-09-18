"""
Android notification adapter.

On Android, background scheduled notifications require a native Flutter plugin
(e.g. flutter_local_notifications). Flet's Python layer does not have direct
access to Android scheduling APIs at this time.

This adapter:
1. Logs notification intent clearly.
2. Shows in-app banners as a fallback when the app is open.
3. Documents the path to full native implementation.

For production Android builds, the recommended approach is:
    - Use a Flet-compatible Flutter plugin for local notifications.
    - OR implement a background service via android.app.AlarmManager
      through Pyjnius (if using Buildozer/Kivy-compatible Python).

This file is intentionally left as a documented stub so the architecture
is in place for the implementation to be plugged in.
"""
from __future__ import annotations

import logging
from datetime import datetime

from src.notifications.base_adapter import NotificationAdapter

logger = logging.getLogger(__name__)


class AndroidNotificationAdapter(NotificationAdapter):
    """
    Android notification adapter.

    Current status: In-app logging fallback.
    Scheduled background notifications require native plugin integration.
    """

    @property
    def platform_name(self) -> str:
        return "Android"

    def is_available(self) -> bool:
        # Available in the sense that we can log, but not schedule natively
        return True

    def send_now(self, notification_id: int, title: str, body: str, data: dict | None = None) -> bool:
        """
        In-app notification. On Android, when the app is open, Flet's
        SnackBar or Banner can serve as the notification. This is handled
        by NotificationService via the on_notification callback.
        """
        logger.info(
            "[Android] Send notification now: id=%d title=%r body=%r", notification_id, title, body
        )
        # The actual in-app display is handled by NotificationService
        return True

    def schedule(self, notification_id: int, remind_at: datetime, title: str, body: str, data: dict | None = None) -> bool:
        """
        Scheduled background notification — requires native plugin.

        Without a native plugin, this logs the intent and returns False
        so NotificationService can inform the user of the limitation.
        """
        logger.warning(
            "[Android] Background notification scheduling is not yet implemented natively. "
            "Reminder id=%d for %s will not fire when app is closed.",
            notification_id, remind_at
        )
        # Return False to signal scheduling is not available
        return False

    def cancel(self, notification_id: int) -> bool:
        logger.info("[Android] Cancel notification: id=%d", notification_id)
        return True

    def cancel_all(self) -> None:
        logger.info("[Android] Cancel all notifications.")
