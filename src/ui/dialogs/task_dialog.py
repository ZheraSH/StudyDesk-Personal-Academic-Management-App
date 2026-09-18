"""
Full task dialog — comprehensive modal for adding or editing an academic task.
"""
from __future__ import annotations
from datetime import datetime, time
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography, TIMEZONE
from src.database.models.task import Task, TaskType, Priority, TaskStatus
from src.services.task_service import TaskService, TaskData
from src.services.course_service import CourseService
from src.utils.datetime_utils import now_local, to_local
from src.utils.i18n import t
from src.ui.components.shared import (
    sd_text_field, sd_dropdown, sd_primary_button, sd_secondary_button,
    sd_error_banner, sd_gap,
)


class TaskDialog(ft.AlertDialog):
    """Modal dialog for full task creation or editing."""

    def __init__(
        self,
        task: Task | None = None,
        on_saved: Callable[[Task], None] | None = None,
    ) -> None:
        self._task = task
        self._on_saved = on_saved
        self._service = TaskService()
        self._course_service = CourseService()

        # Title
        self._title_field = sd_text_field(
            label=t("field_task_title"),
            value=task.title if task else "",
            hint=t("hint_task_title"),
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
        selected_course = str(task.course_id) if task and task.course_id else "none"
        self._course_dropdown = sd_dropdown(
            label=t("field_course"),
            options=course_options,
            value=selected_course,
            expand=True,
        )

        # Task Type
        type_options = [
            ft.dropdown.Option(key=tt.value, text=t(f"task_type_{tt.value.lower()}"))
            for tt in TaskType
        ]
        selected_type = task.task_type.value if task else TaskType.ASSIGNMENT.value
        self._type_dropdown = sd_dropdown(
            label=t("field_task_type"),
            options=type_options,
            value=selected_type,
            expand=True,
        )

        # Priority
        priority_options = [
            ft.dropdown.Option(key=p.value, text=t(f"priority_{p.value.lower()}"))
            for p in Priority
        ]
        selected_priority = task.priority.value if task else Priority.MEDIUM.value
        self._priority_dropdown = sd_dropdown(
            label=t("field_priority"),
            options=priority_options,
            value=selected_priority,
            expand=True,
        )

        # Status
        status_options = [
            ft.dropdown.Option(key=s.value, text=t(f"status_{s.value.lower().replace(' ', '_')}"))
            for s in TaskStatus
        ]
        selected_status = task.status.value if task else TaskStatus.INBOX.value
        self._status_dropdown = sd_dropdown(
            label=t("field_status"),
            options=status_options,
            value=selected_status,
            expand=True,
        )

        # Deadline date and time
        deadline_date_str = ""
        deadline_time_str = "23:59"
        if task and task.deadline:
            loc = to_local(task.deadline)
            deadline_date_str = loc.strftime("%Y-%m-%d")
            deadline_time_str = loc.strftime("%H:%M")

        self._date_field = sd_text_field(
            label=t("field_deadline_date"),
            value=deadline_date_str,
            hint="2026-09-30",
            expand=True,
        )
        self._time_field = sd_text_field(
            label=t("field_deadline_time"),
            value=deadline_time_str,
            hint="23:59",
            expand=True,
        )

        # Estimated duration in minutes
        est_val = str(task.estimated_minutes) if task and task.estimated_minutes else ""
        self._estimated_field = sd_text_field(
            label=t("field_estimated"),
            value=est_val,
            hint=t("hint_estimated"),
            expand=True,
        )

        # Description
        self._desc_field = sd_text_field(
            label=t("field_description"),
            value=task.description if task and task.description else "",
            hint=t("hint_description"),
            multiline=True,
            max_lines=4,
        )

        self._error_container = ft.Column(tight=True)

        content = ft.Container(
            content=ft.Column(
                controls=[
                    self._error_container,
                    self._title_field,
                    ft.Row(
                        controls=[self._course_dropdown, self._type_dropdown],
                        spacing=Spacing.MD,
                    ),
                    ft.Row(
                        controls=[self._priority_dropdown, self._status_dropdown],
                        spacing=Spacing.MD,
                    ),
                    ft.Row(
                        controls=[self._date_field, self._time_field, self._estimated_field],
                        spacing=Spacing.MD,
                    ),
                    self._desc_field,
                ],
                spacing=Spacing.MD,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=540,
            padding=Spacing.MD,
        )

        title_text = t("dlg_edit_task") if task else t("dlg_create_task")

        super().__init__(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, color=Colors.PRIMARY, size=22),
                    ft.Text(title_text, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
                ],
                spacing=Spacing.SM,
            ),
            content=content,
            actions=[
                sd_secondary_button(t("btn_cancel"), on_click=self._close_dialog),
                sd_primary_button(t("btn_save_task"), on_click=self._save_task),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=Radius.LG),
            bgcolor=Colors.SURFACE_RAISED,
        )

    def _close_dialog(self, _: ft.ControlEvent | None = None) -> None:
        self.open = False
        if self.page:
            self.page.update()

    def _parse_deadline(self) -> datetime | None:
        date_str = self._date_field.value.strip()
        if not date_str:
            return None
        time_str = self._time_field.value.strip() or "23:59"
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            return dt.replace(tzinfo=TIMEZONE)
        except ValueError:
            return None

    def _save_task(self, _: ft.ControlEvent) -> None:
        title = self._title_field.value.strip()
        if not title:
            self._show_error(t("err_task_title_required"))
            return

        course_id = (
            int(self._course_dropdown.value)
            if self._course_dropdown.value and self._course_dropdown.value != "none"
            else None
        )

        deadline = None
        if self._date_field.value.strip():
            deadline = self._parse_deadline()
            if not deadline:
                self._show_error(t("err_invalid_deadline_format"))
                return

        estimated_min = None
        if self._estimated_field.value.strip():
            try:
                estimated_min = int(self._estimated_field.value.strip())
            except ValueError:
                self._show_error(t("err_invalid_duration"))
                return

        data = TaskData(
            title=title,
            course_id=course_id,
            task_type=TaskType(self._type_dropdown.value),
            priority=Priority(self._priority_dropdown.value),
            status=TaskStatus(self._status_dropdown.value),
            deadline=deadline,
            estimated_minutes=estimated_min,
            description=self._desc_field.value.strip(),
            is_reschedule=self._task is not None,
        )

        if self._task:
            task, errors = self._service.update(self._task.id, data)
        else:
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
