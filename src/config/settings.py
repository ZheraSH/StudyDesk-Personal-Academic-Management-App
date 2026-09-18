"""
StudyDesk Application Configuration
All constants, paths, and design tokens live here.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ─────────────────────────── App Identity ────────────────────────────

APP_NAME = "StudyDesk"
APP_VERSION = "1.0.0"
APP_ID = "com.studydesk.app"

# ─────────────────────────── Timezone ────────────────────────────────

try:
    TIMEZONE = ZoneInfo("Asia/Jakarta")
except Exception:
    TIMEZONE = timezone(timedelta(hours=7), name="Asia/Jakarta")

# ─────────────────────────── Paths ───────────────────────────────────

def _get_app_data_dir() -> Path:
    """Return a platform-safe application data directory."""
    if "FLET_APP_STORAGE_DATA" in os.environ:
        base = Path(os.environ["FLET_APP_STORAGE_DATA"])
    elif sys.platform == "android" or "ANDROID_ROOT" in os.environ:
        base = Path(os.environ.get("FLET_APP_STORAGE_DATA", "/data/user/0/com.studydesk.app/files"))
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / APP_NAME
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        # Linux / other
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME

    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return base


APP_DATA_DIR: Path = _get_app_data_dir()
DB_PATH: Path = APP_DATA_DIR / "studydesk.db"
ATTACHMENTS_DIR: Path = APP_DATA_DIR / "attachments"
BACKUPS_DIR: Path = APP_DATA_DIR / "backups"
LOGS_DIR: Path = APP_DATA_DIR / "logs"

# Ensure directories exist
for _dir in (ATTACHMENTS_DIR, BACKUPS_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ─────────────────────────── Design Tokens ───────────────────────────

class Colors:
    """All color constants for the StudyDesk design system.
    Muted Royal Purple Skeuomorphism palette.
    """
    # Primary purple family
    PRIMARY = "#6F5A8E"
    PRIMARY_DARK = "#514568"
    PRIMARY_LIGHT = "#9B89B8"
    PRIMARY_LIGHTER = "#C4B8D6"

    # Surface / background
    BACKGROUND = "#F4F1F7"
    SURFACE = "#E8E1EF"
    SURFACE_RAISED = "#EDE8F3"
    SURFACE_INSET = "#DDD5E8"

    # Text
    TEXT = "#302A38"
    TEXT_MUTED = "#746B7D"
    TEXT_DISABLED = "#ADA5B5"
    TEXT_ON_PRIMARY = "#FFFFFF"

    # Border
    BORDER = "#C8BDD4"
    BORDER_LIGHT = "#DDD5E8"
    BORDER_FOCUS = "#6F5A8E"

    # Semantic
    SUCCESS = "#748A77"
    SUCCESS_BG = "#EBF0EB"
    WARNING = "#AD8E61"
    WARNING_BG = "#F5EEE3"
    DANGER = "#A66F78"
    DANGER_BG = "#F2E8EA"
    INFO = "#5E7A9E"
    INFO_BG = "#E5EDF5"

    # Task status
    STATUS_INBOX = "#9B89B8"
    STATUS_PLANNED = "#6F5A8E"
    STATUS_IN_PROGRESS = "#5E7A9E"
    STATUS_COMPLETED = "#748A77"
    STATUS_ARCHIVED = "#ADA5B5"
    STATUS_OVERDUE = "#A66F78"

    # Priority
    PRIORITY_LOW = "#9B89B8"
    PRIORITY_MEDIUM = "#AD8E61"
    PRIORITY_HIGH = "#A66F78"
    PRIORITY_URGENT = "#8B4A56"

    # Schedule type
    SCHEDULE_LECTURE = "#6F5A8E"
    SCHEDULE_PRACTICUM = "#5E7A9E"
    SCHEDULE_OTHER = "#748A77"

    # Shadow / overlay
    SHADOW = "rgba(48, 42, 56, 0.12)"
    SHADOW_DEEP = "rgba(48, 42, 56, 0.20)"
    OVERLAY = "rgba(48, 42, 56, 0.40)"

    # Dark mode (future use)
    DARK_BACKGROUND = "#1E1A24"
    DARK_SURFACE = "#2A2434"
    DARK_TEXT = "#E8E1EF"
    DARK_TEXT_MUTED = "#9B89B8"


class Typography:
    """Font size and weight constants."""
    FONT_FAMILY = "Segoe UI"

    # Sizes
    SIZE_CAPTION = 11
    SIZE_SMALL = 12
    SIZE_BODY = 14
    SIZE_BODY_LARGE = 15
    SIZE_CARD_TITLE = 16
    SIZE_SECTION_TITLE = 18
    SIZE_PAGE_TITLE = 24

    # Weights (Flet uses string weight names)
    WEIGHT_NORMAL = "normal"
    WEIGHT_MEDIUM = "w500"
    WEIGHT_SEMIBOLD = "w600"
    WEIGHT_BOLD = "bold"


class Spacing:
    """Spacing constants in pixels."""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    PAGE_PADDING = 20
    CARD_PADDING = 16
    SECTION_GAP = 20


class Radius:
    """Border radius constants."""
    SM = 6
    MD = 10
    LG = 14
    XL = 18
    PILL = 100


# ─────────────────────────── Feature Config ──────────────────────────

# Reminder presets (minutes before deadline)
REMINDER_PRESETS = {
    "3 days before": 3 * 24 * 60,
    "1 day before": 24 * 60,
    "12 hours before": 12 * 60,
    "3 hours before": 3 * 60,
    "1 hour before": 60,
    "30 minutes before": 30,
    "At deadline": 0,
    "Custom": None,
}

# Focus timer presets (focus_min, break_min)
FOCUS_PRESETS = {
    "15/5": (15, 5),
    "25/5": (25, 5),
    "50/10": (50, 10),
    "Custom": None,
}

DEFAULT_FOCUS_PRESET = "25/5"
DEFAULT_REMINDER_PRESET = "1 day before"

# Task system limits
MAX_CHECKLIST_ITEMS = 50
MAX_ATTACHMENTS_PER_TASK = 20
MAX_REMINDERS_PER_TASK = 5

# Urgency thresholds (hours)
URGENCY_HIGH_HOURS = 24
URGENCY_MODERATE_HOURS = 72    # 3 days
URGENCY_NORMAL_HOURS = 168     # 7 days

# Week start (0 = Monday, 6 = Sunday)
DEFAULT_WEEK_START = 0  # Monday
