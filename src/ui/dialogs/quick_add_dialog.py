"""
Quick add dialog — lightning-fast task creation (title, course, deadline).
Target: created in under 10 seconds.
"""
from __future__ import annotations
from datetime import datetime, time, timedelta
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.task import Task, TaskType, Priority, TaskStatus
from src.services.task_service import TaskService, TaskData
from src.services.course_service import CourseService
from src.utils.datetime_utils import now_local
from src.utils.i18n import t
from src.ui.components.shared import (
    sd_text_field, sd_dropdown, sd_primary_button, sd_secondary_button,
    sd_error_banner, sd_gap,
)


class QuickAddDialog(ft.AlertDialog):
    """Minimal 3-field dialog for rapid task creation."""

    def __init__(
        self,
        on_saved: Callable[[Task], None] | None = None,
        on_more_options: Callable[[], None] | None = None,
    ) -> None:
        self._on_saved = on_saved
        self._on_more_options = on_more_options
        self._service = TaskService()
        self._course_service = CourseService()

        # Title
        self._title_field = sd_text_field(
            label=t("field_task_title"),
            hint=t("hint_quick_task_title"),
            autofocus=True,
            expand=True,
        )

        # Course dropdown
        courses = self._course_service.get_all()
        course_options = [ft.dropdown.Option(key="none", text=t("no_course"))] + [
            ft.dropdown.Option(
                key=str(c.id),
                text=f"{c.code + ' - ' if c.code else ''}{c.name}",
            )
            for c in courses
        ]

        self._course_dropdown = sd_dropdown(
            label=t("field_course"),
            options=course_options,
            value="none",
            expand=True,
        )

        # Quick deadline presets (localized)
        self._deadline_options = [
            ft.dropdown.Option(key="tonight", text=t("deadline_tonight")),
            ft.dropdown.Option(key="tomorrow", text=t("deadline_tomorrow")),
            ft.dropdown.Option(key="3days", text=t("deadline_3days")),
            ft.dropdown.Option(key="nextweek", text=t("deadline_nextweek")),
            ft.dropdown.Option(key="none", text=t("deadline_none")),
        ]
        self._deadline_dropdown = sd_dropdown(
            label=t("field_deadline"),
            options=self._deadline_options,
            value="tomorrow",
            expand=True,
        )

        self._error_container = ft.Column(tight=True)

        content = ft.Container(
            content=ft.Column(
                controls=[
                    self._error_container,
                    self._title_field,
                    ft.Row(
                        controls=[self._course_dropdown, self._deadline_dropdown],
                        spacing=Spacing.MD,
                    ),
                ],
                spacing=Spacing.MD,
                tight=True,
            ),
            width=480,
            padding=Spacing.MD,
        )

        actions: list[ft.Control] = [
            sd_secondary_button(t("btn_cancel"), on_click=self._close_dialog),
        ]
        if self._on_more_options:
            actions.append(
                ft.TextButton(
                    t("btn_more_details"),
                    on_click=self._handle_more_options,
                    style=ft.ButtonStyle(color=Colors.PRIMARY),
                )
            )
        actions.append(sd_primary_button(t("btn_add_task"), on_click=self._save_task))

        super().__init__(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FLASH_ON, color=Colors.PRIMARY, size=22),
                    ft.Text(t("dlg_quick_add_title"), size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
                ],
                spacing=Spacing.SM,
            ),
            content=content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=Radius.LG),
            bgcolor=Colors.SURFACE_RAISED,
        )

    def _close_dialog(self, _: ft.ControlEvent | None = None) -> None:
        self.open = False
        if self.page:
            self.page.update()

    def _handle_more_options(self, _: ft.ControlEvent) -> None:
        self._close_dialog()
        if self._on_more_options:
            self._on_more_options()

    def _calculate_deadline(self) -> datetime | None:
        now = now_local()
        choice = self._deadline_dropdown.value
        if choice == "tonight":
            return now.replace(hour=23, minute=59, second=0, microsecond=0)
        elif choice == "tomorrow":
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=0, microsecond=0)
        elif choice == "3days":
            return (now + timedelta(days=3)).replace(hour=23, minute=59, second=0, microsecond=0)
        elif choice == "nextweek":
            return (now + timedelta(days=7)).replace(hour=23, minute=59, second=0, microsecond=0)
        return None

    def _save_task(self, _: ft.ControlEvent) -> None:
        title = self._title_field.value.strip()
        if not title:
            self._show_error(t("err_task_title_empty"))
            return

        course_id = (
            int(self._course_dropdown.value)
            if self._course_dropdown.value and self._course_dropdown.value != "none"
            else None
        )
        deadline = self._calculate_deadline()

        data = TaskData(
            title=title,
            course_id=course_id,
            task_type=TaskType.ASSIGNMENT,
            priority=Priority.MEDIUM,
            status=TaskStatus.INBOX,
            deadline=deadline,
        )

        task, errors = self._service.create(data)
        if errors:
            self._show_error(errors[0])
            return

        self._close_dialog()
        if self._on_saved and task:
            self._on_saved(task)

    def _show_error(self, message: str) -> None:
        self._error_container.controls = [sd_error_banner(message), sd_gap(Spacing.SM)]
        self._error_container.update()
