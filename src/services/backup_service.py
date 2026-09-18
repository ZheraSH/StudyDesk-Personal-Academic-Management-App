"""Backup and restore service for the StudyDesk database."""
from __future__ import annotations

import csv
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

from src.config.settings import DB_PATH, BACKUPS_DIR
from src.utils.datetime_utils import now_local

logger = logging.getLogger(__name__)


class BackupService:
    def backup_database(self, dest_path: str | Path | None = None) -> tuple[Path | None, str]:
        """Copy the SQLite database to a backup location.

        If dest_path is None, creates a timestamped file in the backups dir.
        """
        try:
            if not DB_PATH.exists():
                return None, "Database file not found. Nothing to back up."

            if dest_path is None:
                timestamp = now_local().strftime("%Y%m%d_%H%M%S")
                dest_path = BACKUPS_DIR / f"studydesk_backup_{timestamp}.db"

            dest = Path(dest_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DB_PATH, dest)
            logger.info("Database backed up to %s", dest)
            return dest, ""
        except Exception as e:
            logger.error("Backup failed: %s", e)
            return None, f"Backup failed: {e}"

    def restore_database(self, src_path: str | Path) -> tuple[bool, str]:
        """Restore the database from a backup file.

        Creates a backup of the current DB before replacing it.
        """
        try:
            src = Path(src_path)
            if not src.exists():
                return False, "Backup file not found."

            if not src.suffix == ".db":
                return False, "Invalid backup file. Expected a .db file."

            # Backup current DB before overwriting
            if DB_PATH.exists():
                self.backup_database()

            shutil.copy2(src, DB_PATH)
            logger.info("Database restored from %s", src)
            return True, "Database restored successfully. Please restart the application."
        except Exception as e:
            logger.error("Restore failed: %s", e)
            return False, f"Restore failed: {e}"

    def export_tasks_csv(self, dest_path: str | Path | None = None) -> tuple[Path | None, str]:
        """Export all tasks to a CSV file."""
        try:
            from src.database.connection import get_db
            from src.database.repositories.task_repository import TaskRepository

            if dest_path is None:
                timestamp = now_local().strftime("%Y%m%d_%H%M%S")
                dest_path = BACKUPS_DIR / f"studydesk_tasks_{timestamp}.csv"

            dest = Path(dest_path)

            with get_db() as session:
                repo = TaskRepository(session)
                tasks = repo.get_filtered(include_completed=True, include_archived=True)

            with open(dest, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Title", "Course", "Type", "Priority", "Status",
                    "Deadline", "Estimated (min)", "Description", "Created At"
                ])
                for t in tasks:
                    writer.writerow([
                        t.id,
                        t.title,
                        t.course.name if t.course else "",
                        t.task_type.value,
                        t.priority.value,
                        t.status.value,
                        t.deadline.isoformat() if t.deadline else "",
                        t.estimated_minutes or "",
                        (t.description or "").replace("\n", " "),
                        t.created_at.isoformat(),
                    ])

            return dest, ""
        except Exception as e:
            logger.error("CSV export failed: %s", e)
            return None, f"Export failed: {e}"

    def export_all_json(self, dest_path: str | Path | None = None) -> tuple[Path | None, str]:
        """Export all data to a JSON file."""
        try:
            from src.database.connection import get_db
            from src.database.repositories.task_repository import TaskRepository
            from src.database.repositories.course_repository import CourseRepository
            from src.database.repositories.schedule_repository import ScheduleRepository
            from src.database.repositories.semester_repository import SemesterRepository

            if dest_path is None:
                timestamp = now_local().strftime("%Y%m%d_%H%M%S")
                dest_path = BACKUPS_DIR / f"studydesk_export_{timestamp}.json"

            dest = Path(dest_path)
            data: dict = {}

            with get_db() as session:
                # Tasks
                task_repo = TaskRepository(session)
                tasks = task_repo.get_filtered(include_completed=True, include_archived=True)
                data["tasks"] = [
                    {
                        "id": t.id,
                        "title": t.title,
                        "course": t.course.name if t.course else None,
                        "task_type": t.task_type.value,
                        "priority": t.priority.value,
                        "status": t.status.value,
                        "deadline": t.deadline.isoformat() if t.deadline else None,
                        "estimated_minutes": t.estimated_minutes,
                        "description": t.description,
                        "created_at": t.created_at.isoformat(),
                        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    }
                    for t in tasks
                ]

                # Courses
                course_repo = CourseRepository(session)
                courses = course_repo.get_all_with_semester()
                data["courses"] = [
                    {
                        "id": c.id,
                        "name": c.name,
                        "code": c.code,
                        "lecturer": c.lecturer,
                        "room": c.room,
                    }
                    for c in courses
                ]

                # Semesters
                sem_repo = SemesterRepository(session)
                semesters = sem_repo.get_all()
                data["semesters"] = [
                    {
                        "id": sm.id,
                        "name": sm.name,
                        "academic_year": sm.academic_year,
                        "is_active": sm.is_active,
                        "start_date": sm.start_date.isoformat() if sm.start_date else None,
                        "end_date": sm.end_date.isoformat() if sm.end_date else None,
                    }
                    for sm in semesters
                ]

                # Schedules
                sched_repo = ScheduleRepository(session)
                schedules = sched_repo.get_all_active()
                data["schedules"] = [
                    {
                        "id": s.id,
                        "course_id": s.course_id,
                        "day_of_week": s.day_of_week,
                        "start_time": s.start_time.strftime("%H:%M"),
                        "end_time": s.end_time.strftime("%H:%M"),
                        "type": s.schedule_type.value,
                        "room": s.room,
                    }
                    for s in schedules
                ]

            data["exported_at"] = now_local().isoformat()
            data["app_version"] = "1.0.0"

            with open(dest, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return dest, ""
        except Exception as e:
            logger.error("JSON export failed: %s", e)
            return None, f"Export failed: {e}"

    def export_tasks_json(self, dest_path: str | Path | None = None) -> tuple[Path | None, str]:
        return self.export_all_json(dest_path)
