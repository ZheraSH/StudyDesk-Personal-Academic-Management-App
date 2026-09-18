"""Notification adapter factory — selects correct adapter for current platform."""
from __future__ import annotations

import sys
import logging

from src.notifications.base_adapter import NotificationAdapter

logger = logging.getLogger(__name__)

_adapter_instance: NotificationAdapter | None = None


def get_adapter() -> NotificationAdapter:
    """Return the correct notification adapter for the current platform."""
    global _adapter_instance
    if _adapter_instance is not None:
        return _adapter_instance

    platform = sys.platform

    if platform == "android":
        from src.notifications.android_adapter import AndroidNotificationAdapter
        _adapter_instance = AndroidNotificationAdapter()
    elif platform == "win32":
        from src.notifications.windows_adapter import WindowsNotificationAdapter
        _adapter_instance = WindowsNotificationAdapter()
    elif platform in ("darwin", "linux"):
        # macOS and Linux: use plyer as well
        from src.notifications.windows_adapter import WindowsNotificationAdapter
        _adapter_instance = WindowsNotificationAdapter()
    else:
        # Unknown platform: use a null adapter that logs only
        from src.notifications.android_adapter import AndroidNotificationAdapter
        _adapter_instance = AndroidNotificationAdapter()

    logger.info("Notification adapter: %s", _adapter_instance.platform_name)
    return _adapter_instance
