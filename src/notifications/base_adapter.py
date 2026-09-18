"""Abstract notification adapter base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class NotificationAdapter(ABC):
    """Platform-agnostic notification interface.

    Concrete implementations provide Windows and Android behavior.
    The NotificationService uses only this interface.
    """

    @abstractmethod
    def send_now(self, notification_id: int, title: str, body: str, data: dict | None = None) -> bool:
        """Send an immediate notification. Returns True on success."""
        ...

    @abstractmethod
    def schedule(self, notification_id: int, remind_at: datetime, title: str, body: str, data: dict | None = None) -> bool:
        """Schedule a notification for a future time. Returns True on success."""
        ...

    @abstractmethod
    def cancel(self, notification_id: int) -> bool:
        """Cancel a previously scheduled notification."""
        ...

    @abstractmethod
    def cancel_all(self) -> None:
        """Cancel all pending notifications."""
        ...

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Human-readable platform name for logging."""
        ...

    def is_available(self) -> bool:
        """Return True if this adapter can deliver notifications on current platform."""
        return True
