"""Checklist service — subtask management."""
from __future__ import annotations

import logging

from src.database.connection import get_db
from src.database.models.task_checklist import TaskChecklist
from src.database.repositories.task_checklist_repository import TaskChecklistRepository
from src.config.settings import MAX_CHECKLIST_ITEMS

logger = logging.getLogger(__name__)


class ChecklistService:
    def get_by_task(self, task_id: int) -> list[TaskChecklist]:
        try:
            with get_db() as session:
                repo = TaskChecklistRepository(session)
                return repo.get_by_task(task_id)
        except Exception as e:
            logger.error("Failed to get checklist for task %d: %s", task_id, e)
            return []

    def get_progress(self, task_id: int) -> tuple[int, int]:
        """Return (done, total) for a task's checklist."""
        try:
            with get_db() as session:
                repo = TaskChecklistRepository(session)
                return repo.get_progress(task_id)
        except Exception as e:
            logger.error("Failed to get checklist progress for task %d: %s", task_id, e)
            return 0, 0

    def add_item(self, task_id: int, title: str) -> tuple[TaskChecklist | None, str]:
        title = title.strip()
        if not title:
            return None, "Checklist item cannot be empty."

        try:
            with get_db() as session:
                repo = TaskChecklistRepository(session)

                # Enforce limit
                existing = repo.get_by_task(task_id)
                if len(existing) >= MAX_CHECKLIST_ITEMS:
                    return None, f"Maximum {MAX_CHECKLIST_ITEMS} checklist items allowed."

                max_order = repo.get_max_sort_order(task_id)
                item = TaskChecklist(
                    task_id=task_id,
                    title=title,
                    is_completed=False,
                    sort_order=max_order + 1,
                )
                repo.add(item)
                return item, ""
        except Exception as e:
            logger.error("Failed to add checklist item to task %d: %s", task_id, e)
            return None, "Unable to add checklist item. Please try again."

    def toggle_item(self, item_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = TaskChecklistRepository(session)
                item = repo.get_by_id(item_id)
                if not item:
                    return False, "Item not found."
                item.is_completed = not item.is_completed
                return True, ""
        except Exception as e:
            logger.error("Failed to toggle checklist item %d: %s", item_id, e)
            return False, "Unable to update checklist item. Please try again."

    def update_item(self, item_id: int, title: str) -> tuple[bool, str]:
        title = title.strip()
        if not title:
            return False, "Checklist item cannot be empty."
        try:
            with get_db() as session:
                repo = TaskChecklistRepository(session)
                item = repo.get_by_id(item_id)
                if not item:
                    return False, "Item not found."
                item.title = title
                return True, ""
        except Exception as e:
            logger.error("Failed to update checklist item %d: %s", item_id, e)
            return False, "Unable to update item. Please try again."

    def delete_item(self, item_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = TaskChecklistRepository(session)
                item = repo.get_by_id(item_id)
                if not item:
                    return False, "Item not found."
                repo.delete(item)
                return True, ""
        except Exception as e:
            logger.error("Failed to delete checklist item %d: %s", item_id, e)
            return False, "Unable to delete checklist item. Please try again."
