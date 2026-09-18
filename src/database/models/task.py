"""Task model with full academic task management fields."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin
from src.database.models.task_checklist import TaskChecklist


class TaskType(str, enum.Enum):
    ASSIGNMENT = "Assignment"
    PRESENTATION = "Presentation"
    REPORT = "Report"
    PROJECT = "Project"
    QUIZ = "Quiz"
    EXAM = "Exam"
    OTHER = "Other"


class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

    @property
    def sort_order(self) -> int:
        """Lower number = higher priority for sorting."""
        return {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}[self.value]


class TaskStatus(str, enum.Enum):
    INBOX = "Inbox"
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

    @property
    def is_active(self) -> bool:
        return self in (TaskStatus.INBOX, TaskStatus.PLANNED, TaskStatus.IN_PROGRESS)

    @property
    def is_terminal(self) -> bool:
        return self in (TaskStatus.COMPLETED, TaskStatus.ARCHIVED)


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), nullable=False, default=TaskType.ASSIGNMENT
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority), nullable=False, default=Priority.MEDIUM
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.INBOX
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    course: Mapped["Course | None"] = relationship(  # type: ignore[name-defined]
        "Course", back_populates="tasks", lazy="joined"
    )
    checklists: Mapped[list["TaskChecklist"]] = relationship(  # type: ignore[name-defined]
        "TaskChecklist",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskChecklist.sort_order",
    )
    reminders: Mapped[list["Reminder"]] = relationship(  # type: ignore[name-defined]
        "Reminder", back_populates="task", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(  # type: ignore[name-defined]
        "Attachment", back_populates="task", cascade="all, delete-orphan"
    )
    focus_sessions: Mapped[list["FocusSession"]] = relationship(  # type: ignore[name-defined]
        "FocusSession", back_populates="task"
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
