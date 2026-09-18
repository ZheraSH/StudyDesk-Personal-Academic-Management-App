"""Course repository."""
from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from src.database.models.course import Course
from src.database.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: Session) -> None:
        super().__init__(Course, session)

    def get_all_with_semester(self) -> list[Course]:
        return (
            self.session.query(Course)
            .options(joinedload(Course.semester))
            .order_by(Course.name)
            .all()
        )

    def get_by_semester(self, semester_id: int) -> list[Course]:
        return (
            self.session.query(Course)
            .filter(Course.semester_id == semester_id)
            .order_by(Course.name)
            .all()
        )

    def get_active_semester_courses(self) -> list[Course]:
        """Return courses that belong to the currently active semester."""
        from src.database.models.semester import Semester
        return (
            self.session.query(Course)
            .join(Semester, Course.semester_id == Semester.id)
            .filter(Semester.is_active == True)
            .order_by(Course.name)
            .all()
        )

    def search(self, query: str) -> list[Course]:
        q = f"%{query}%"
        return (
            self.session.query(Course)
            .filter(Course.name.ilike(q))
            .order_by(Course.name)
            .all()
        )
