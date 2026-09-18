"""Settings service — application configuration key/value store."""
from __future__ import annotations

import logging

from src.database.connection import get_db
from src.database.repositories.app_setting_repository import AppSettingRepository
from src.config.settings import DEFAULT_REMINDER_PRESET, DEFAULT_FOCUS_PRESET

logger = logging.getLogger(__name__)

# Setting keys — never use raw strings elsewhere
KEY_PROFILE_NAME = "profile_name"
KEY_ACTIVE_SEMESTER_ID = "active_semester_id"
KEY_THEME = "theme"
KEY_DEFAULT_REMINDER = "default_reminder"
KEY_WEEK_START = "week_start"
KEY_TIME_FORMAT = "time_format"
KEY_NOTIFICATIONS_ENABLED = "notifications_enabled"
KEY_LANGUAGE = "language"


class SettingsService:
    def get(self, key: str, default: str | None = None) -> str | None:
        try:
            with get_db() as session:
                repo = AppSettingRepository(session)
                value = repo.get(key)
                return value if value is not None else default
        except Exception as e:
            logger.error("Failed to get setting %r: %s", key, e)
            return default

    def set(self, key: str, value: str | None) -> bool:
        try:
            with get_db() as session:
                repo = AppSettingRepository(session)
                repo.set(key, value)
            return True
        except Exception as e:
            logger.error("Failed to set setting %r: %s", key, e)
            return False

    def get_profile_name(self) -> str:
        return self.get(KEY_PROFILE_NAME, "Student") or "Student"

    def set_profile_name(self, name: str) -> bool:
        return self.set(KEY_PROFILE_NAME, name.strip() or "Student")

    def get_active_semester_id(self) -> int | None:
        val = self.get(KEY_ACTIVE_SEMESTER_ID)
        return int(val) if val and val.isdigit() else None

    def set_active_semester_id(self, semester_id: int | None) -> bool:
        return self.set(KEY_ACTIVE_SEMESTER_ID, str(semester_id) if semester_id else None)

    def get_default_reminder(self) -> str:
        return self.get(KEY_DEFAULT_REMINDER, DEFAULT_REMINDER_PRESET) or DEFAULT_REMINDER_PRESET

    def set_default_reminder(self, preset: str) -> bool:
        return self.set(KEY_DEFAULT_REMINDER, preset)

    def get_week_start(self) -> int:
        val = self.get(KEY_WEEK_START, "0")
        return int(val) if val and val.isdigit() else 0

    def set_week_start(self, day: int) -> bool:
        return self.set(KEY_WEEK_START, str(day))

    def get_notifications_enabled(self) -> bool:
        val = self.get(KEY_NOTIFICATIONS_ENABLED, "true")
        return val.lower() == "true" if val else True

    def set_notifications_enabled(self, enabled: bool) -> bool:
        return self.set(KEY_NOTIFICATIONS_ENABLED, "true" if enabled else "false")

    def get_language(self) -> str:
        lang = self.get(KEY_LANGUAGE, "id") or "id"
        from src.utils.i18n import set_language as set_i18n_lang
        set_i18n_lang(lang)
        return lang

    def set_language(self, lang: str) -> bool:
        from src.utils.i18n import set_language as set_i18n_lang
        set_i18n_lang(lang)
        return self.set(KEY_LANGUAGE, lang)


# Module-level singleton
_settings_service: SettingsService | None = None


def get_settings_service() -> SettingsService:
    global _settings_service
    if _settings_service is None:
        _settings_service = SettingsService()
    return _settings_service
