"""TaskChecklist repository."""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.database.models.task_checklist import TaskChecklist
from src.database.repositories.base_repository import BaseRepository


class TaskChecklistRepository(BaseRepository[TaskChecklist]):
    def __init__(self, session: Session) -> None:
        super().__init__(TaskChecklist, session)

    def get_by_task(self, task_id: int) -> list[TaskChecklist]:
        return (
            self.session.query(TaskChecklist)
            .filter(TaskChecklist.task_id == task_id)
            .order_by(TaskChecklist.sort_order)
            .all()
        )

    def get_progress(self, task_id: int) -> tuple[int, int]:
        """Return (completed_count, total_count) for a task's checklist."""
        items = self.get_by_task(task_id)
        total = len(items)
        done = sum(1 for i in items if i.is_completed)
        return done, total

    def get_max_sort_order(self, task_id: int) -> int:
        from sqlalchemy import func
        result = (
            self.session.query(func.max(TaskChecklist.sort_order))
            .filter(TaskChecklist.task_id == task_id)
            .scalar()
        )
        return result or 0
