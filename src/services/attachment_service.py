"""Attachment service — file management for tasks."""
from __future__ import annotations

import logging
from pathlib import Path

from src.database.connection import get_db
from src.database.models.attachment import Attachment
from src.database.repositories.attachment_repository import AttachmentRepository
from src.utils.file_utils import (
    copy_to_app_storage,
    get_file_size,
    get_file_type,
    open_file,
)
from src.config.settings import MAX_ATTACHMENTS_PER_TASK

logger = logging.getLogger(__name__)


class AttachmentService:
    def get_by_task(self, task_id: int) -> list[Attachment]:
        try:
            with get_db() as session:
                repo = AttachmentRepository(session)
                return repo.get_by_task(task_id)
        except Exception as e:
            logger.error("Failed to get attachments for task %d: %s", task_id, e)
            return []

    def add_attachment(self, task_id: int, source_path: str) -> tuple[Attachment | None, str]:
        """Copy a file into managed storage and record it in the database."""
        try:
            with get_db() as session:
                repo = AttachmentRepository(session)

                # Enforce limit
                existing = repo.get_by_task(task_id)
                if len(existing) >= MAX_ATTACHMENTS_PER_TASK:
                    return None, f"Maximum {MAX_ATTACHMENTS_PER_TASK} attachments per task."

            src = Path(source_path)
            if not src.exists():
                return None, f"File not found: {src.name}"

            managed_path = copy_to_app_storage(src, task_id)
            file_size = get_file_size(managed_path)
            file_type = get_file_type(managed_path)

            with get_db() as session:
                attachment = Attachment(
                    task_id=task_id,
                    file_name=src.name,
                    file_path=str(managed_path),
                    file_type=file_type,
                    file_size=file_size,
                )
                repo = AttachmentRepository(session)
                repo.add(attachment)
                return attachment, ""
        except Exception as e:
            logger.error("Failed to add attachment for task %d: %s", task_id, e)
            return None, "Unable to attach file. Please try again."

    def remove_attachment(self, attachment_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = AttachmentRepository(session)
                attachment = repo.get_by_id(attachment_id)
                if not attachment:
                    return False, "Attachment not found."

                file_path = Path(attachment.file_path)
                repo.delete(attachment)

            # Remove the file from managed storage
            if file_path.exists():
                file_path.unlink(missing_ok=True)

            return True, ""
        except Exception as e:
            logger.error("Failed to remove attachment %d: %s", attachment_id, e)
            return False, "Unable to remove attachment. Please try again."

    def open_attachment(self, attachment_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = AttachmentRepository(session)
                attachment = repo.get_by_id(attachment_id)
                if not attachment:
                    return False, "Attachment not found."
                file_path = attachment.file_path

            open_file(file_path)
            return True, ""
        except FileNotFoundError:
            return False, "File no longer exists. It may have been moved or deleted."
        except Exception as e:
            logger.error("Failed to open attachment %d: %s", attachment_id, e)
            return False, "Unable to open file. Please try again."
