"""
Tests for BackupService: CSV export, JSON export, and database backup.
"""
from pathlib import Path
import json
import csv
import pytest

from src.services.backup_service import BackupService
from src.services.task_service import TaskService, TaskData


def test_export_tasks_csv(db_session, sample_course, tmp_path):
    task_service = TaskService()
    backup_service = BackupService()

    task_service.create(TaskData(title="Exportable Task 1", course_id=sample_course.id))
    task_service.create(TaskData(title="Exportable Task 2", course_id=sample_course.id))

    csv_dest = tmp_path / "test_tasks.csv"
    exported_path, err = backup_service.export_tasks_csv(csv_dest)

    assert err == ""
    assert exported_path is not None
    assert exported_path.exists()

    with open(exported_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) >= 3  # Header + 2 tasks


def test_export_tasks_json(db_session, sample_course, tmp_path):
    task_service = TaskService()
    backup_service = BackupService()

    task_service.create(TaskData(title="JSON Export Task", course_id=sample_course.id))

    json_dest = tmp_path / "test_data.json"
    exported_path, err = backup_service.export_tasks_json(json_dest)

    assert err == ""
    assert exported_path is not None
    assert exported_path.exists()

    with open(exported_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)
        assert "tasks" in data
        assert "semesters" in data
        assert "courses" in data
