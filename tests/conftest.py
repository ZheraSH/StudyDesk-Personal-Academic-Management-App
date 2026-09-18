"""
Pytest fixtures for StudyDesk test suite.
Uses an isolated in-memory SQLite database with SQLAlchemy 2.x.
"""
from __future__ import annotations
import os
import pytest
from datetime import datetime, time, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.config.settings import TIMEZONE
from src.database.models.base import Base
from src.database.models.semester import Semester
from src.database.models.course import Course
from src.database.models.schedule import Schedule, ScheduleType
from src.database.models.task import Task, TaskType, Priority, TaskStatus
import src.database.connection as db_conn


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory SQLite database for each test."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=True,
        expire_on_commit=False,
        bind=test_engine,
    )

    original_engine = db_conn._engine
    original_session_factory = db_conn._SessionFactory
    db_conn._engine = test_engine
    db_conn._SessionFactory = TestingSessionLocal

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)
        test_engine.dispose()
        db_conn._engine = original_engine
        db_conn._SessionFactory = original_session_factory


@pytest.fixture
def sample_semester(db_session: Session) -> Semester:
    sem = Semester(
        name="Fall 2026",
        academic_year="2026/2027",
        is_active=True,
    )
    db_session.add(sem)
    db_session.commit()
    db_session.refresh(sem)
    return sem


@pytest.fixture
def sample_course(db_session: Session, sample_semester: Semester) -> Course:
    course = Course(
        name="Operating Systems",
        code="CS301",
        lecturer="Dr. Alan Turing",
        room="Hall 404",
        color="#6F5A8E",
        semester_id=sample_semester.id,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def sample_task(db_session: Session, sample_course: Course) -> Task:
    now = datetime.now(TIMEZONE)
    task = Task(
        title="Kernel Module Assignment",
        course_id=sample_course.id,
        task_type=TaskType.ASSIGNMENT,
        priority=Priority.HIGH,
        status=TaskStatus.INBOX,
        deadline=now + timedelta(days=2),
        estimated_minutes=120,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
