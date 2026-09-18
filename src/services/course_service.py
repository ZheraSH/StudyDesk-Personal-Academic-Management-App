"""Course service — business logic for course management."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from src.database.connection import get_db
from src.database.models.course import Course
from src.database.repositories.course_repository import CourseRepository
from src.database.repositories.semester_repository import SemesterRepository
from src.utils.validation import validate_course

logger = logging.getLogger(__name__)


@dataclass
class CourseData:
    name: str
    code: str = ""
    lecturer: str = ""
    room: str = ""
    color: str = "#6F5A8E"
    notes: str = ""
    semester_id: int | None = None


class CourseService:
    def get_all(self) -> list[Course]:
        try:
            with get_db() as session:
                repo = CourseRepository(session)
                return repo.get_all_with_semester()
        except Exception as e:
            logger.error("Failed to get courses: %s", e)
            return []

    def get_active_semester_courses(self) -> list[Course]:
        try:
            with get_db() as session:
                repo = CourseRepository(session)
                return repo.get_active_semester_courses()
        except Exception as e:
            logger.error("Failed to get active semester courses: %s", e)
            return []

    def get_by_id(self, course_id: int) -> Course | None:
        try:
            with get_db() as session:
                repo = CourseRepository(session)
                return repo.get_by_id(course_id)
        except Exception as e:
            logger.error("Failed to get course %d: %s", course_id, e)
            return None

    def create(self, data: CourseData) -> tuple[Course | None, list[str]]:
        errors = validate_course(vars(data))
        if errors:
            return None, errors
        try:
            with get_db() as session:
                course = Course(
                    name=data.name.strip(),
                    code=(data.code or "").strip() or None,
                    lecturer=(data.lecturer or "").strip() or None,
                    room=(data.room or "").strip() or None,
                    color=data.color or "#6F5A8E",
                    notes=(data.notes or "").strip() or None,
                    semester_id=data.semester_id,
                )
                repo = CourseRepository(session)
                repo.add(course)
                return course, []
        except Exception as e:
            logger.error("Failed to create course: %s", e)
            return None, ["Unable to save course. Please try again."]

    def update(self, course_id: int, data: CourseData) -> tuple[Course | None, list[str]]:
        errors = validate_course(vars(data))
        if errors:
            return None, errors
        try:
            with get_db() as session:
                repo = CourseRepository(session)
                course = repo.get_by_id(course_id)
                if not course:
                    return None, ["Course not found."]
                course.name = data.name.strip()
                course.code = (data.code or "").strip() or None
                course.lecturer = (data.lecturer or "").strip() or None
                course.room = (data.room or "").strip() or None
                course.color = data.color or "#6F5A8E"
                course.notes = (data.notes or "").strip() or None
                course.semester_id = data.semester_id
                return course, []
        except Exception as e:
            logger.error("Failed to update course %d: %s", course_id, e)
            return None, ["Unable to update course. Please try again."]

    def delete(self, course_id: int) -> tuple[bool, str]:
        try:
            with get_db() as session:
                repo = CourseRepository(session)
                course = repo.get_by_id(course_id)
                if not course:
                    return False, "Course not found."
                repo.delete(course)
                return True, ""
        except Exception as e:
            logger.error("Failed to delete course %d: %s", course_id, e)
            return False, "Unable to delete course. Please try again."
