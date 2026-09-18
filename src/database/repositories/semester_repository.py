"""Semester repository."""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.database.models.semester import Semester
from src.database.repositories.base_repository import BaseRepository


class SemesterRepository(BaseRepository[Semester]):
    def __init__(self, session: Session) -> None:
        super().__init__(Semester, session)

    def get_active(self) -> Semester | None:
        return self.session.query(Semester).filter(Semester.is_active == True).first()

    def deactivate_all(self) -> None:
        self.session.query(Semester).update({Semester.is_active: False})
        self.session.flush()

    def set_active(self, semester_id: int) -> Semester | None:
        self.deactivate_all()
        semester = self.get_by_id(semester_id)
        if semester:
            semester.is_active = True
            self.session.flush()
        return semester
