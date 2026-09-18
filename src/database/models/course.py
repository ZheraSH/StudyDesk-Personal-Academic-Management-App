"""Course model."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    semester_id: Mapped[int | None] = mapped_column(
        ForeignKey("semesters.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lecturer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#6F5A8E", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    semester: Mapped["Semester | None"] = relationship(  # type: ignore[name-defined]
        "Semester", back_populates="courses", lazy="joined"
    )
    schedules: Mapped[list["Schedule"]] = relationship(  # type: ignore[name-defined]
        "Schedule", back_populates="course", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(  # type: ignore[name-defined]
        "Task", back_populates="course"
    )

    def __repr__(self) -> str:
        return f"<Course id={self.id} name={self.name!r} code={self.code!r}>"
