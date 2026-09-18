"""
Tests for CourseService: course creation, update, listing, and deletion.
"""
import pytest

from src.services.course_service import CourseService, CourseData


def test_create_and_update_course(db_session, sample_semester):
    service = CourseService()

    data = CourseData(
        name="Linear Algebra",
        code="MATH201",
        lecturer="Prof. Gauss",
        room="Hall A",
        color="#5E7A9E",
        semester_id=sample_semester.id,
    )
    course, errors = service.create(data)

    assert errors == []
    assert course is not None
    assert course.id is not None
    assert course.name == "Linear Algebra"

    # Update course
    update_data = CourseData(
        name="Linear Algebra & Matrix Theory",
        code="MATH201",
        lecturer="Prof. Gauss",
        room="Hall B",
        color="#748A77",
        semester_id=sample_semester.id,
    )
    updated, errs = service.update(course.id, update_data)
    assert errs == []
    assert updated.name == "Linear Algebra & Matrix Theory"
    assert updated.room == "Hall B"


def test_delete_course(db_session, sample_course):
    service = CourseService()
    success, msg = service.delete(sample_course.id)
    assert success is True

    fetched = service.get_by_id(sample_course.id)
    assert fetched is None
