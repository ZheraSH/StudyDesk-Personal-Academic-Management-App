"""
End-to-end integration test verifying all core StudyDesk features:
- Course & Semester management
- Schedule creation & weekly lookup
- Task lifecycle, checklists & reminders
- Focus session recording with lazy-load safety (no DetachedInstanceError)
- Statistics and workload health
- i18n Indonesian and English translation
- Backup & export (JSON and CSV)
"""
import pytest
from datetime import datetime, time, timedelta, timezone

from src.services.course_service import CourseService, CourseData
from src.services.schedule_service import ScheduleService, ScheduleData
from src.services.task_service import TaskService, TaskData
from src.services.checklist_service import ChecklistService
from src.services.reminder_service import ReminderService
from src.services.focus_service import FocusService
from src.services.statistics_service import StatisticsService
from src.services.settings_service import get_settings_service
from src.services.backup_service import BackupService
from src.database.models.task import TaskType, Priority, TaskStatus
from src.database.models.schedule import ScheduleType
from src.utils.datetime_utils import now_local
from src.utils.i18n import t, set_language, get_language


def test_e2e_complete_student_flow(db_session, tmp_path):
    # ── 1. Settings & Localization ──────────────────────────────
    settings = get_settings_service()
    settings.set_profile_name("Budi Santoso")
    assert settings.get_profile_name() == "Budi Santoso"

    # Test i18n
    settings.set_language("id")
    assert get_language() == "id"
    assert t("nav_dashboard") == "Beranda"
    assert t("nav_tasks") == "Tugas"
    assert t("nav_schedule") == "Jadwal"

    settings.set_language("en")
    assert get_language() == "en"
    assert t("nav_dashboard") == "Dashboard"
    assert t("nav_tasks") == "Tasks"

    # Switch back to Indonesian
    settings.set_language("id")

    # ── 2. Course Creation ──────────────────────────────────────
    course_svc = CourseService()
    course, errors = course_svc.create(
        CourseData(
            name="Pemrograman Web",
            code="IF301",
            color="#4f46e5",
        )
    )
    assert not errors
    assert course is not None
    assert course.id is not None

    # ── 3. Schedule Creation ────────────────────────────────────
    sched_svc = ScheduleService()
    sched, errors = sched_svc.create(
        ScheduleData(
            course_id=course.id,
            day_of_week=0,  # Monday
            start_time=time(8, 0),
            end_time=time(10, 0),
            room="Lab Komputer 3",
            schedule_type=ScheduleType.LECTURE,
        )
    )
    assert not errors
    assert sched is not None

    # Verify conflict detection
    conflict_sched, conflict_errs = sched_svc.create(
        ScheduleData(
            course_id=course.id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
    )
    assert conflict_sched is None
    assert any("conflict" in err.lower() for err in conflict_errs)

    # ── 4. Task Lifecycle ───────────────────────────────────────
    task_svc = TaskService()
    deadline = now_local() + timedelta(days=3)
    task, errors = task_svc.create(
        TaskData(
            title="Tugas Besar Sistem Web",
            course_id=course.id,
            task_type=TaskType.PROJECT,
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            deadline=deadline,
            estimated_minutes=120,
        )
    )
    assert not errors
    assert task is not None
    assert task.course.name == "Pemrograman Web"

    # Checklists
    chk_svc = ChecklistService()
    item1, err1 = chk_svc.add_item(task.id, "Setup database schema")
    item2, err2 = chk_svc.add_item(task.id, "Implement REST API")
    assert err1 == "" and item1 is not None
    assert err2 == "" and item2 is not None

    chk_svc.toggle_item(item1.id)
    items = chk_svc.get_by_task(task.id)
    assert len(items) == 2
    assert any(i.is_completed for i in items)

    # Reminders
    rem_svc = ReminderService()
    from src.database.models.reminder import ReminderType
    rem, err = rem_svc.create_reminder(task.id, ReminderType.ONE_DAY, deadline)
    assert err == ""
    assert rem is not None

    # ── 5. Focus Session & Detached Instance Safety ─────────────
    focus_svc = FocusService()
    fs, err = focus_svc.start_session(task_id=task.id)
    assert err == ""
    assert fs is not None

    completed_fs, err = focus_svc.end_session(
        session_id=fs.id,
        completed=True,
    )
    assert err == ""
    assert completed_fs.completed is True

    # Crucial Test: querying recent sessions outside the DB session
    # MUST NOT raise DetachedInstanceError when accessing session.task.title
    recent = focus_svc.get_recent(limit=5)
    assert len(recent) >= 1
    session_item = recent[0]
    # Accessing relationship:
    assert session_item.task is not None
    assert session_item.task.title == "Tugas Besar Sistem Web"

    # ── 6. Statistics Calculation ───────────────────────────────
    stats_svc = StatisticsService()
    t_stats = stats_svc.get_task_stats()
    assert t_stats.active >= 1
    assert t_stats.completed == 0

    # Mark task as completed
    task_svc.toggle_complete(task.id)
    t_stats_after = stats_svc.get_task_stats()
    assert t_stats_after.completed >= 1

    weekly_stats = stats_svc.get_weekly_stats()
    assert weekly_stats.focus_minutes >= 1

    # ── 7. Data Backup & Export ─────────────────────────────────
    backup_svc = BackupService()
    json_path = tmp_path / "backup.json"
    csv_path = tmp_path / "tasks.csv"

    exported_json, err_json = backup_svc.export_all_json(json_path)
    assert err_json == ""
    assert exported_json is not None
    assert exported_json.exists()
    assert exported_json.stat().st_size > 0

    exported_csv, err_csv = backup_svc.export_tasks_csv(csv_path)
    assert err_csv == ""
    assert exported_csv is not None
    assert exported_csv.exists()
    assert exported_csv.stat().st_size > 0
