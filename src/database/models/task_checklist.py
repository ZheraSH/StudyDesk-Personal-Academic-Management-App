"""TaskChecklist model — subtasks for a Task."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class TaskChecklist(Base, TimestampMixin):
    __tablename__ = "task_checklists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    task: Mapped["Task"] = relationship(  # type: ignore[name-defined]
        "Task", back_populates="checklists"
    )

    def __repr__(self) -> str:
        return (
            f"<TaskChecklist id={self.id} task_id={self.task_id} "
            f"title={self.title!r} done={self.is_completed}>"
        )
