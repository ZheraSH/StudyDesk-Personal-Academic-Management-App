"""Task repository — filter, search, sort, and query tasks."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from src.database.models.task import Priority, Task, TaskStatus, TaskType
from src.database.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: Session) -> None:
        super().__init__(Task, session)

    def get_by_id_full(self, task_id: int) -> Task | None:
        """Load task with all relationships eagerly."""
        return (
            self.session.query(Task)
            .options(
                joinedload(Task.course),
                joinedload(Task.checklists),
                joinedload(Task.reminders),
                joinedload(Task.attachments),
            )
            .filter(Task.id == task_id)
            .first()
        )

    def get_all_active(self) -> list[Task]:
        """Tasks that are not completed or archived."""
        return (
            self.session.query(Task)
            .options(joinedload(Task.course))
            .filter(
                Task.status.in_([TaskStatus.INBOX, TaskStatus.PLANNED, TaskStatus.IN_PROGRESS])
            )
            .order_by(Task.deadline.nullslast())
            .all()
        )

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
        query = self.session.query(Task).options(joinedload(Task.course))

        # Status filter
        status_filter = list(status) if status else []
        if not include_completed:
            status_filter = [s for s in status_filter if s != TaskStatus.COMPLETED]
        if not include_archived:
            status_filter = [s for s in status_filter if s != TaskStatus.ARCHIVED]
        if status_filter:
            query = query.filter(Task.status.in_(status_filter))

        # Priority filter
        if priority:
            query = query.filter(Task.priority.in_(priority))

        # Course filter
        if course_id is not None:
            query = query.filter(Task.course_id == course_id)

        # Task type filter
        if task_type is not None:
            query = query.filter(Task.task_type == task_type)

        # Search
        if search:
            q = f"%{search}%"
            query = query.filter(
                or_(Task.title.ilike(q), Task.description.ilike(q))
            )

        # Sort
        sort_map = {
            "deadline": Task.deadline,
            "priority": Task.priority,
            "created_at": Task.created_at,
            "status": Task.status,
        }
        sort_col = sort_map.get(sort_by, Task.deadline)
        if sort_asc:
            query = query.order_by(sort_col.nullslast())
        else:
            query = query.order_by(sort_col.desc().nullslast())

        return query.all()

    def get_overdue(self, now: datetime) -> list[Task]:
        return (
            self.session.query(Task)
            .options(joinedload(Task.course))
            .filter(
                Task.deadline < now,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.ARCHIVED]),
            )
            .order_by(Task.deadline)
            .all()
        )

    def get_urgent(self, now: datetime, within_hours: int = 24) -> list[Task]:
        from datetime import timedelta
        cutoff = now + timedelta(hours=within_hours)
        return (
            self.session.query(Task)
            .options(joinedload(Task.course))
            .filter(
                Task.deadline >= now,
                Task.deadline <= cutoff,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.ARCHIVED]),
            )
            .order_by(Task.deadline)
            .all()
        )

    def get_upcoming(self, now: datetime, within_days: int = 7) -> list[Task]:
        from datetime import timedelta
        cutoff = now + timedelta(days=within_days)
        return (
            self.session.query(Task)
            .options(joinedload(Task.course))
            .filter(
                Task.deadline >= now,
                Task.deadline <= cutoff,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.ARCHIVED]),
            )
            .order_by(Task.deadline)
            .all()
        )

    def get_completed_this_week(self, week_start: datetime, week_end: datetime) -> list[Task]:
        return (
            self.session.query(Task)
            .filter(
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at >= week_start,
                Task.completed_at <= week_end,
            )
            .all()
        )
