"""
File utilities for StudyDesk.
All path resolution is platform-safe — no hardcoded Windows paths.
"""
from __future__ import annotations

import mimetypes
import os
import shutil
import sys
from pathlib import Path

from src.config.settings import ATTACHMENTS_DIR


def get_attachments_dir_for_task(task_id: int) -> Path:
    """Return the managed storage directory for a specific task's attachments."""
    task_dir = ATTACHMENTS_DIR / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir


def copy_to_app_storage(src_path: str | Path, task_id: int) -> Path:
    """Copy a file into managed app storage and return the new path.

    Uses the original filename. If a file with the same name exists,
    a numeric suffix is added to avoid collisions.
    """
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    dest_dir = get_attachments_dir_for_task(task_id)
    dest = dest_dir / src.name

    # Avoid overwriting: add numeric suffix
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{src.stem}_{counter}{src.suffix}"
        counter += 1

    shutil.copy2(src, dest)
    return dest


def get_file_type(path: str | Path) -> str:
    """Return a normalized file type/extension string (e.g. 'pdf', 'docx')."""
    suffix = Path(path).suffix.lower().lstrip(".")
    return suffix or "file"


def get_mime_type(path: str | Path) -> str:
    """Return the MIME type of a file."""
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def get_file_size(path: str | Path) -> int | None:
    """Return file size in bytes, or None if file does not exist."""
    p = Path(path)
    if p.exists():
        return p.stat().st_size
    return None


def open_file(path: str | Path) -> None:
    """Open a file with the system default application, platform-safely."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    if sys.platform == "win32":
        os.startfile(str(p))
    elif sys.platform == "darwin":
        import subprocess
        subprocess.Popen(["open", str(p)])
    elif sys.platform == "linux":
        import subprocess
        subprocess.Popen(["xdg-open", str(p)])
    elif sys.platform == "android":
        # On Android, Flet uses a different mechanism.
        # This is handled by the Android attachment adapter.
        _open_file_android(p)
    else:
        raise RuntimeError(f"Unsupported platform for file open: {sys.platform}")


def _open_file_android(path: Path) -> None:
    """Android-specific file open using Flet's platform channel.
    Falls back gracefully if unavailable.
    """
    try:
        import flet as ft
        # On Android, use the platform's file viewer intent
        # This requires a Flet plugin or bridge — logged as informational
        # for now, with a fallback to just logging the path
        import logging
        logging.getLogger(__name__).info(
            "Android file open requested for: %s — implement via Flet platform channel.", path
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Cannot open file on Android: %s", e)


def is_safe_path(path: str | Path, base_dir: Path) -> bool:
    """Verify a path is within a base directory (prevents path traversal)."""
    try:
        Path(path).resolve().relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False


def delete_task_attachments(task_id: int) -> None:
    """Delete all attachment files for a task from managed storage."""
    task_dir = ATTACHMENTS_DIR / str(task_id)
    if task_dir.exists():
        shutil.rmtree(task_dir)
