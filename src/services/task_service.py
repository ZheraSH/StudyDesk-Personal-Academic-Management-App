"""Task service — core business logic for task management."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from src.database.connection import get_db
from src.database.models.task import Priority, Task, TaskStatus, TaskType
from src.database.repositories.task_repository import TaskRepository
from src.utils.datetime_utils import now_local
from src.utils.validation import validate_task

logger = logging.getLogger(__name__)


@dataclass
class TaskData:
    title: str
    course_id: int | None = None
    task_type: TaskType = TaskType.ASSIGNMENT
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.INBOX
    deadline: datetime | None = None
    estimated_minutes: int | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    is_reschedule: bool = False  # Allow past deadline when rescheduling


class TaskService:
    def get_all_active(self) -> list[Task]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                return repo.get_all_active()
        except Exception as e:
            logger.error("Failed to get active tasks: %s", e)
            return []

    def get_by_id(self, task_id: int) -> Task | None:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                return repo.get_by_id_full(task_id)
        except Exception as e:
            logger.error("Failed to get task %d: %s", task_id, e)
            return None

    def get_filtered(
        self,
        status: list[TaskStatus] | None = None,
        priority: list[Priority] | None = None,
        course_id: int | None = None,
        task_type: TaskType | None = None,
        search: str | None = None,
        sort_by: str = "deadline",
        sort_asc: bool = True,
        include_completed: bool = False,
        include_archived: bool = False,
    ) -> list[Task]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                return repo.get_filtered(
                    status=status,
                    priority=priority,
                    course_id=course_id,
                    task_type=task_type,
                    search=search,
                    sort_by=sort_by,
                    sort_asc=sort_asc,
                    include_completed=include_completed,
                    include_archived=include_archived,
                )
        except Exception as e:
            logger.error("Failed to get filtered tasks: %s", e)
            return []

    def get_overdue(self) -> list[Task]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                return repo.get_overdue(now_local())
        except Exception as e:
            logger.error("Failed to get overdue tasks: %s", e)
            return []

    def get_urgent(self, within_hours: int = 24) -> list[Task]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                return repo.get_urgent(now_local(), within_hours)
        except Exception as e:
            logger.error("Failed to get urgent tasks: %s", e)
            return []

    def get_upcoming(self, within_days: int = 7) -> list[Task]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                return repo.get_upcoming(now_local(), within_days)
        except Exception as e:
            logger.error("Failed to get upcoming tasks: %s", e)
            return []

    def create(self, data: TaskData) -> tuple[Task | None, list[str]]:
        errors = validate_task(
            {
                "title": data.title,
                "deadline": data.deadline,
                "estimated_minutes": data.estimated_minutes,
                "planned_start": data.planned_start,
                "planned_end": data.planned_end,
            },
            is_reschedule=data.is_reschedule,
        )
        if errors:
            return None, errors

        try:
            with get_db() as session:
                task = Task(
                    title=data.title.strip(),
                    course_id=data.course_id,
                    task_type=data.task_type,
                    description=(data.description or "").strip() or None,
                    priority=data.priority,
                    status=data.status,
                    deadline=data.deadline,
                    estimated_minutes=data.estimated_minutes,
                    planned_start=data.planned_start,
                    planned_end=data.planned_end,
                )
                repo = TaskRepository(session)
                repo.add(task)
                saved = repo.get_by_id_full(task.id)
                return saved or task, []
        except Exception as e:
            logger.error("Failed to create task: %s", e)
            return None, ["Unable to save task. Your data was not changed. Please try again."]

    def update(self, task_id: int, data: TaskData) -> tuple[Task | None, list[str]]:
        errors = validate_task(
            {
                "title": data.title,
                "deadline": data.deadline,
                "estimated_minutes": data.estimated_minutes,
                "planned_start": data.planned_start,
                "planned_end": data.planned_end,
            },
            is_reschedule=data.is_reschedule,
        )
        if errors:
            return None, errors

        try:
            with get_db() as session:
                repo = TaskRepository(session)
                task = repo.get_by_id(task_id)
                if not task:
                    return None, ["Task not found."]
                task.title = data.title.strip()
                task.course_id = data.course_id
                task.task_type = data.task_type
                task.description = (data.description or "").strip() or None
                task.priority = data.priority
                task.status = data.status
                task.deadline = data.deadline
                task.estimated_minutes = data.estimated_minutes
                task.planned_start = data.planned_start
                task.planned_end = data.planned_end
                saved = repo.get_by_id_full(task.id)
                return saved or task, []
        except Exception as e:
            logger.error("Failed to update task %d: %s", task_id, e)
            return None, ["Unable to update task. Please try again."]

    def complete(self, task_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                task = repo.get_by_id(task_id)
                if not task:
                    return False, "Task not found."
                task.status = TaskStatus.COMPLETED
                task.completed_at = now_local()
                return True, ""
        except Exception as e:
            logger.error("Failed to complete task %d: %s", task_id, e)
            return False, "Unable to complete task. Please try again."

    def toggle_complete(self, task_id: int) -> tuple[Task | None, str]:
        """Toggle task status between COMPLETED and IN_PROGRESS."""
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                task = repo.get_by_id(task_id)
                if not task:
                    return None, "Task not found."
                if task.status == TaskStatus.COMPLETED:
                    task.status = TaskStatus.IN_PROGRESS
                    task.completed_at = None
                else:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = now_local()
                return task, ""
        except Exception as e:
            logger.error("Failed to toggle task %d: %s", task_id, e)
            return None, "Unable to update task. Please try again."

    def archive(self, task_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                task = repo.get_by_id(task_id)
                if not task:
                    return False, "Task not found."
                task.status = TaskStatus.ARCHIVED
                return True, ""
        except Exception as e:
            logger.error("Failed to archive task %d: %s", task_id, e)
            return False, "Unable to archive task. Please try again."

    def reopen(self, task_id: int) -> tuple[bool, str]:
        """Re-open a completed or archived task."""
        try:
            with get_db() as session:
                repo = TaskRepository(session)
                task = repo.get_by_id(task_id)
                if not task:
                    return False, "Task not found."
                task.status = TaskStatus.INBOX
                task.completed_at = None
                return True, ""
        except Exception as e:
            logger.error("Failed to reopen task %d: %s", task_id, e)
            return False, "Unable to reopen task. Please try again."

    def delete(self, task_id: int) -> tuple[bool, str]:
        """Permanently delete a task and all associated data."""
        try:
            from src.utils.file_utils import delete_task_attachments
            with get_db() as session:
                repo = TaskRepository(session)
                task = repo.get_by_id(task_id)
                if not task:
                    return False, "Task not found."
                repo.delete(task)
            # Clean up attachment files
            delete_task_attachments(task_id)
            return True, ""
        except Exception as e:
            logger.error("Failed to delete task %d: %s", task_id, e)
            return False, "Unable to delete task. Please try again."
