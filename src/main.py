"""
StudyDesk — Personal Academic Management Application.
Main entry point for desktop and mobile.
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft

from src.config.settings import (
    APP_NAME, APP_VERSION, Colors, Spacing, Radius, Typography,
    LOGS_DIR, DB_PATH
)
from src.database.connection import init_db, get_db
from src.database.models.semester import Semester
from src.database.repositories.semester_repository import SemesterRepository
from src.database.repositories.app_setting_repository import AppSettingRepository
from src.services.settings_service import KEY_PROFILE_NAME, KEY_ACTIVE_SEMESTER_ID, get_settings_service
from src.services.reminder_service import ReminderService
from src.services.notification_service import NotificationService
from src.ui.theme.theme import get_theme
from src.ui.components.sidebar import Sidebar
from src.ui.components.bottom_nav import build_bottom_nav
from src.ui.pages.dashboard_page import DashboardPage
from src.ui.pages.schedule_page import SchedulePage
from src.ui.pages.tasks_page import TasksPage
from src.ui.pages.task_detail_page import TaskDetailPage
from src.ui.pages.focus_page import FocusPage
from src.ui.pages.statistics_page import StatisticsPage
from src.ui.pages.settings_page import SettingsPage
from src.ui.dialogs.quick_add_dialog import QuickAddDialog
from src.ui.dialogs.task_dialog import TaskDialog
from src.ui.dialogs.schedule_dialog import ScheduleDialog
from src.utils.i18n import t

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "studydesk.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("StudyDesk")


def seed_defaults_if_needed() -> None:
    """Seed initial semester and default settings on first run."""
    try:
        with get_db() as session:
            sem_repo = SemesterRepository(session)
            semesters = sem_repo.get_all()
            if not semesters:
                default_sem = Semester(
                    name="Current Semester",
                    academic_year="2026/2027",
                    is_active=True,
                )
                sem_repo.add(default_sem)
                logger.info("Initialized default semester: %s", default_sem.name)

            setting_repo = AppSettingRepository(session)
            if not setting_repo.get(KEY_PROFILE_NAME):
                setting_repo.set(KEY_PROFILE_NAME, "Zhera")
    except Exception as e:
        logger.error("Error during initial data seed: %s", e)


class StudyDeskApp:
    """Main Application Controller."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.current_route = "dashboard"
        self.selected_task_id: int | None = None
        self.focus_task_id: int | None = None

        # Detect platform layout
        self.is_mobile = page.platform in (
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        )

        # Page configuration
        page.title = f"{APP_NAME} — Personal Academic Management"
        page.theme = get_theme()
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = Colors.BACKGROUND
        page.padding = 0

        # Window sizing for desktop
        if not self.is_mobile:
            page.window.width = 1200
            page.window.height = 800
            page.window.min_width = 860
            page.window.min_height = 600

        # Notifications
        self.notification_service = NotificationService(on_in_app_notification=self._show_in_app_toast)
        try:
            ReminderService().reconcile_on_startup()
            self.notification_service.reschedule_all_pending()
        except Exception as e:
            logger.error("Startup reminder reconciliation error: %s", e)

        # Initialize language
        get_settings_service().get_language()

        # Layout containers
        self.content_area = ft.Container(expand=True)
        self.sidebar: Sidebar | None = None

        self._build_layout()
        self.navigate("dashboard")

    def _build_layout(self) -> None:
        if self.is_mobile:
            self.bottom_nav = build_bottom_nav(
                current_route=self.current_route,
                on_navigate=self.navigate,
            )
            self.page.navigation_bar = self.bottom_nav
            self.page.add(self.content_area)
        else:
            self.sidebar = Sidebar(
                current_route=self.current_route,
                on_navigate=self.navigate,
            )
            layout = ft.Row(
                controls=[
                    self.sidebar,
                    ft.VerticalDivider(width=1, color=Colors.BORDER_LIGHT),
                    self.content_area,
                ],
                expand=True,
                spacing=0,
            )
            self.page.add(layout)

    def navigate(self, route: str, **kwargs) -> None:
        # Handle colon-delimited routes like "task_detail:42" or "focus:5"
        if ":" in route:
            base, _, param = route.partition(":")
            try:
                param_int = int(param)
            except ValueError:
                param_int = None
            if base == "task_detail" and param_int:
                self.open_task_detail(param_int)
                return
            elif base == "focus" and param_int:
                self.start_focus_for_task(param_int)
                return
            route = base

        self.current_route = route
        logger.info("Navigating to: %s", route)

        if not self.is_mobile and self.sidebar:
            self.sidebar.update_route(route)
        elif self.is_mobile and hasattr(self, "bottom_nav"):
            from src.ui.components.bottom_nav import MOBILE_NAV_ITEMS
            routes = [item[0] for item in MOBILE_NAV_ITEMS]
            if route in routes:
                self.bottom_nav.selected_index = routes.index(route)
                try:
                    self.bottom_nav.update()
                except Exception:
                    pass

        if route == "dashboard":
            page_widget = DashboardPage(
                on_navigate=self.navigate,
                on_add_task=self.open_quick_add,
            )
        elif route == "schedule":
            page_widget = SchedulePage(
                on_add_schedule=self.open_add_schedule,
                on_edit_schedule=self.open_edit_schedule,
            )
        elif route == "tasks":
            page_widget = TasksPage(
                on_add_task=self.open_quick_add,
                on_open_task=self.open_task_detail,
            )
        elif route == "task_detail":
            task_id = kwargs.get("task_id", self.selected_task_id)
            if task_id:
                page_widget = TaskDetailPage(
                    task_id=task_id,
                    on_back=lambda: self.navigate("tasks"),
                    on_edit=self.open_edit_task,
                    on_start_focus=self.start_focus_for_task,
                )
            else:
                self.navigate("tasks")
                return
        elif route == "focus":
            task_id = kwargs.get("task_id", self.focus_task_id)
            page_widget = FocusPage(initial_task_id=task_id)
        elif route == "statistics":
            page_widget = StatisticsPage()
        elif route == "settings":
            page_widget = SettingsPage(
                on_course_updated=lambda: None,
                on_language_changed=self.on_language_changed,
            )
        else:
            page_widget = DashboardPage(
                on_navigate=self.navigate,
                on_add_task=self.open_quick_add,
            )

        self.content_area.content = page_widget
        self.page.update()

    def on_language_changed(self, new_lang: str) -> None:
        logger.info("Application language changed: %s", new_lang)
        if not self.is_mobile and self.sidebar:
            self.sidebar.update_route(self.current_route)
        elif self.is_mobile and hasattr(self, "bottom_nav"):
            self.bottom_nav = build_bottom_nav(
                current_route=self.current_route,
                on_navigate=self.navigate,
            )
            self.page.navigation_bar = self.bottom_nav
            self.page.update()

    def open_quick_add(self) -> None:
        def on_saved(task) -> None:
            self._show_toast(t("toast_task_created", title=task.title))
            self.navigate(self.current_route)

        dlg = QuickAddDialog(
            on_saved=on_saved,
            on_more_options=self.open_full_add_task,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def open_full_add_task(self) -> None:
        def on_saved(task) -> None:
            self._show_toast(t("toast_task_created", title=task.title))
            self.navigate(self.current_route)

        dlg = TaskDialog(task=None, on_saved=on_saved)
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def open_edit_task(self, task_id: int) -> None:
        from src.services.task_service import TaskService
        task = TaskService().get_by_id(task_id)
        if not task:
            return

        def on_saved(updated_task) -> None:
            self._show_toast(t("toast_task_updated", title=updated_task.title))
            if self.current_route == "task_detail":
                self.navigate("task_detail", task_id=task_id)
            else:
                self.navigate(self.current_route)

        dlg = TaskDialog(task=task, on_saved=on_saved)
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def open_task_detail(self, task_id: int) -> None:
        self.selected_task_id = task_id
        self.navigate("task_detail", task_id=task_id)

    def start_focus_for_task(self, task_id: int) -> None:
        self.focus_task_id = task_id
        self.navigate("focus", task_id=task_id)

    def open_add_schedule(self) -> None:
        def on_saved(schedule) -> None:
            info = f"{schedule.day_name} {schedule.start_time.strftime('%H:%M')}"
            self._show_toast(t("toast_schedule_added", info=info))
            self.navigate("schedule")

        dlg = ScheduleDialog(schedule=None, on_saved=on_saved)
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def open_edit_schedule(self, schedule_id: int) -> None:
        from src.database.connection import get_db
        from src.database.repositories.schedule_repository import ScheduleRepository
        with get_db() as session:
            sched = ScheduleRepository(session).get_by_id(schedule_id)

        if not sched:
            return

        def on_saved(updated) -> None:
            info = f"{updated.day_name} {updated.start_time.strftime('%H:%M')}"
            self._show_toast(t("toast_schedule_updated", info=info))
            self.navigate("schedule")

        dlg = ScheduleDialog(schedule=sched, on_saved=on_saved)
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _show_toast(self, message: str) -> None:
        snack = ft.SnackBar(
            content=ft.Text(message, color=Colors.TEXT_ON_PRIMARY),
            bgcolor=Colors.PRIMARY_DARK,
            duration=3000,
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    def _show_in_app_toast(self, title: str, body: str) -> None:
        snack = ft.SnackBar(
            content=ft.Column(
                controls=[
                    ft.Text(title, weight=ft.FontWeight.BOLD, color=Colors.TEXT_ON_PRIMARY),
                    ft.Text(body, size=Typography.SIZE_SMALL, color=Colors.TEXT_ON_PRIMARY),
                ],
                spacing=2,
                tight=True,
            ),
            bgcolor=Colors.PRIMARY,
            duration=5000,
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()


def main(page: ft.Page) -> None:
    # Initialize DB schema
    init_db()
    seed_defaults_if_needed()

    # Launch app
    StudyDeskApp(page)


if __name__ == "__main__":
    ft.run(main)
