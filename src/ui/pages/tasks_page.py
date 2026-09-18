"""
Tasks page — task list with filtering, searching, and sorting.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.task import Priority, Task, TaskStatus, TaskType
from src.services.task_service import TaskService
from src.services.course_service import CourseService
from src.ui.components.shared import (
    sd_card, sd_section_title, sd_body, sd_muted, sd_caption,
    sd_gap, sd_empty_state, sd_badge, sd_primary_button,
    sd_status_badge, sd_priority_badge, sd_urgency_badge,
    sd_text_field, sd_dropdown, safe_update,
)
from src.utils.datetime_utils import format_remaining, get_urgency_level, now_local
from src.utils.i18n import t


class TasksPage(ft.Column):
    """Task list page with full filter/search/sort capability."""

    def __init__(
        self,
        on_add_task: Callable,
        on_open_task: Callable[[int], None],
    ) -> None:
        self._on_add_task = on_add_task
        self._on_open_task = on_open_task
        self._task_service = TaskService()
        self._course_service = CourseService()

        # Filter state
        self._search = ""
        self._sort_by = "deadline"
        self._sort_asc = True
        self._filter_status: list[TaskStatus] = [
            TaskStatus.INBOX, TaskStatus.PLANNED, TaskStatus.IN_PROGRESS
        ]
        self._include_completed = False
        self._include_archived = False

        super().__init__(
            controls=[],
            expand=True,
            spacing=0,
        )
        self.refresh()

    def refresh(self) -> None:
        self.controls = [self._build()]
        safe_update(self)

    def _build(self) -> ft.Control:
        tasks = self._task_service.get_filtered(
            search=self._search or None,
            sort_by=self._sort_by,
            sort_asc=self._sort_asc,
            include_completed=self._include_completed,
            include_archived=self._include_archived,
        )

        header = self._build_header()
        filter_row = self._build_filter_row()
        task_list = self._build_task_list(tasks)

        return ft.Column(
            controls=[header, filter_row, task_list],
            expand=True,
            spacing=0,
        )

    def _build_header(self) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        t("tasks_title"),
                        size=Typography.SIZE_PAGE_TITLE,
                        weight=ft.FontWeight.W_600,
                        color=Colors.TEXT,
                        expand=True,
                    ),
                    sd_primary_button(t("btn_new_task"), on_click=lambda _: self._on_add_task(), icon=ft.Icons.ADD),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.only(
                left=Spacing.PAGE_PADDING,
                right=Spacing.PAGE_PADDING,
                top=Spacing.PAGE_PADDING,
                bottom=Spacing.MD,
            ),
        )

    def _build_filter_row(self) -> ft.Control:
        border = {
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=ft.BorderRadius.all(Radius.MD),
                side=ft.BorderSide(1, Colors.BORDER),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=ft.BorderRadius.all(Radius.MD),
                side=ft.BorderSide(1.5, Colors.PRIMARY),
            ),
        }
        search_field = ft.TextField(
            hint_text=t("search_tasks_hint"),
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            value=self._search,
            border=border,
            bgcolor=Colors.SURFACE_INSET,
            content_padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
            dense=True,
            expand=True,
        )

        sort_options = [
            ft.dropdown.Option("deadline", t("sort_deadline")),
            ft.dropdown.Option("priority", t("sort_priority")),
            ft.dropdown.Option("created_at", t("sort_created")),
            ft.dropdown.Option("status", t("sort_status")),
        ]
        sort_dropdown = ft.Dropdown(
            options=sort_options,
            value=self._sort_by,
            on_select=self._on_sort_change,
            border=border,
            bgcolor=Colors.SURFACE_INSET,
            content_padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
            dense=True,
            width=140,
        )

        show_completed_switch = ft.Switch(
            label=t("filter_completed"),
            value=self._include_completed,
            on_change=self._on_toggle_completed,
            active_color=Colors.PRIMARY,
            label_text_style=ft.TextStyle(size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[search_field, sd_gap(Spacing.SM), sort_dropdown],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            show_completed_switch,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=Spacing.SM,
                tight=True,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.PAGE_PADDING, vertical=Spacing.SM),
            bgcolor=Colors.BACKGROUND,
        )

    def _build_task_list(self, tasks: list[Task]) -> ft.Control:
        if not tasks:
            empty = sd_empty_state(
                icon=ft.Icons.ASSIGNMENT_OUTLINED,
                title=t("empty_tasks_title"),
                subtitle=t("empty_tasks_subtitle"),
                action=sd_primary_button(t("btn_add_first_task"), on_click=lambda _: self._on_add_task(), icon=ft.Icons.ADD),
            )
            return ft.Container(content=empty, expand=True)

        # Group by urgency category
        overdue = [item for item in tasks if item.deadline and get_urgency_level(item.deadline) == "overdue"]
        rest = [item for item in tasks if item not in overdue]

        items: list[ft.Control] = []
        if overdue:
            items.append(
                ft.Container(
                    content=ft.Text(
                        t("section_overdue_tasks", count=len(overdue)),
                        size=Typography.SIZE_SMALL,
                        color=Colors.DANGER,
                        weight=ft.FontWeight.W_600,
                        style=ft.TextStyle(letter_spacing=1.1),
                    ),
                    padding=ft.Padding.only(left=Spacing.PAGE_PADDING, top=Spacing.MD, bottom=Spacing.XS),
                )
            )
            for item in overdue:
                items.append(self._build_task_card(item))

        if rest:
            items.append(
                ft.Container(
                    content=ft.Text(
                        t("section_active_tasks", count=len(rest)),
                        size=Typography.SIZE_SMALL,
                        color=Colors.TEXT_MUTED,
                        weight=ft.FontWeight.W_600,
                        style=ft.TextStyle(letter_spacing=1.1),
                    ),
                    padding=ft.Padding.only(left=Spacing.PAGE_PADDING, top=Spacing.MD, bottom=Spacing.XS),
                )
            )
            for item in rest:
                items.append(self._build_task_card(item))

        return ft.ListView(
            controls=items,
            spacing=0,
            padding=ft.Padding.only(bottom=Spacing.XXXL),
            expand=True,
        )

    def _build_task_card(self, task: Task) -> ft.Control:
        urgency = get_urgency_level(task.deadline)
        remaining = format_remaining(task.deadline)
        course_name = task.course.name if task.course else "—"

        is_overdue = urgency == "overdue"
        is_completed = task.status == TaskStatus.COMPLETED

        URGENCY_COLOR = {
            "overdue": Colors.DANGER,
            "critical": Colors.DANGER,
            "high": Colors.WARNING,
            "moderate": Colors.TEXT_MUTED,
            "normal": Colors.TEXT_MUTED,
            "none": Colors.TEXT_MUTED,
        }
        time_color = URGENCY_COLOR.get(urgency, Colors.TEXT_MUTED)

        def on_complete(e: ft.ControlEvent, current_t: Task = task) -> None:
            self._task_service.complete(current_t.id)
            self.refresh()

        task_type_raw = task.task_type.value if hasattr(task.task_type, "value") else str(task.task_type)
        task_type_label = t(f"task_type_{task_type_raw.lower()}")

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Completion checkbox
                    ft.Checkbox(
                        value=is_completed,
                        on_change=on_complete,
                        active_color=Colors.SUCCESS,
                        check_color=Colors.TEXT_ON_PRIMARY,
                        fill_color={ft.ControlState.SELECTED: Colors.SUCCESS},
                    ),
                    # Main content
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        task.title,
                                        size=Typography.SIZE_BODY,
                                        weight=ft.FontWeight.W_600,
                                        color=Colors.TEXT_DISABLED if is_completed else Colors.TEXT,
                                        expand=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1,
                                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if is_completed else None),
                                    ),
                                    sd_priority_badge(task.priority.value, small=True),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                controls=[
                                    sd_caption(course_name),
                                    sd_caption("·"),
                                    ft.Text(task_type_label, size=Typography.SIZE_CAPTION, color=Colors.TEXT_MUTED),
                                    sd_caption("·"),
                                    ft.Text(remaining, size=Typography.SIZE_CAPTION, color=time_color),
                                ],
                                spacing=Spacing.XS,
                                tight=True,
                            ),
                        ],
                        spacing=2,
                        tight=True,
                        expand=True,
                    ),
                    # Arrow
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Colors.BORDER, size=18),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.SM,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.PAGE_PADDING, vertical=Spacing.MD),
            bgcolor=Colors.DANGER_BG if is_overdue else "transparent",
            border=ft.Border.only(bottom=ft.BorderSide(1, Colors.BORDER_LIGHT)),
            on_click=lambda _, current_t=task: self._on_open_task(current_t.id),
            ink=True,
        )

    # ── Event handlers ────────────────────────────────────────────────

    def _on_search_change(self, e: ft.ControlEvent) -> None:
        self._search = e.control.value or ""
        self.refresh()

    def _on_sort_change(self, e: ft.ControlEvent) -> None:
        self._sort_by = e.control.value or "deadline"
        self.refresh()

    def _on_toggle_completed(self, e: ft.ControlEvent) -> None:
        self._include_completed = e.control.value
        self.refresh()
