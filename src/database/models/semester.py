"""Semester model."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class Semester(Base, TimestampMixin):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    academic_year: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    courses: Mapped[list["Course"]] = relationship(  # type: ignore[name-defined]
        "Course", back_populates="semester", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Semester id={self.id} name={self.name!r} active={self.is_active}>"
