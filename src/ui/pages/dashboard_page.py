"""
Dashboard page — personal academic command center.
Information hierarchy: Next class → Today's schedule → Urgent → Upcoming → Load.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.schedule import Schedule
from src.database.models.task import Task, TaskStatus
from src.services.schedule_service import ScheduleService
from src.services.task_service import TaskService
from src.services.statistics_service import StatisticsService
from src.services.settings_service import get_settings_service
from src.ui.components.shared import (
    sd_card, sd_section_title, sd_body, sd_muted, sd_caption,
    sd_gap, sd_empty_state, sd_urgency_badge, sd_priority_badge,
    sd_badge, safe_update,
)
from src.utils.datetime_utils import (
    now_local, format_deadline, format_remaining,
    format_time, get_urgency_level, greeting_for_hour,
    format_full_header_date,
)
from src.utils.i18n import t


class DashboardPage(ft.Column):
    """Dashboard — the main landing page of StudyDesk."""

    def __init__(
        self,
        on_navigate: Callable[[str], None],
        on_add_task: Callable,
    ) -> None:
        self._on_navigate = on_navigate
        self._on_add_task = on_add_task
        self._schedule_service = ScheduleService()
        self._task_service = TaskService()
        self._stats_service = StatisticsService()
        self._settings = get_settings_service()

        super().__init__(
            controls=[self._build()],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True,
        )

    def refresh(self) -> None:
        self.controls = [self._build()]
        safe_update(self)

    def _build(self) -> ft.Control:
        now = now_local()
        profile_name = self._settings.get_profile_name()
        if now.hour < 11:
            greeting = t("greeting_morning")
        elif now.hour < 15:
            greeting = t("greeting_afternoon")
        elif now.hour < 18:
            greeting = t("greeting_evening")
        else:
            greeting = t("greeting_night")
        date_str = format_full_header_date(now)

        next_class = self._schedule_service.get_next_class()
        today_schedules = self._schedule_service.get_today()
        overdue_tasks = self._task_service.get_overdue()
        urgent_tasks = self._task_service.get_urgent(within_hours=24)
        upcoming_tasks = self._task_service.get_upcoming(within_days=7)
        stats = self._stats_service.get_task_stats()

        sections: list[ft.Control] = [
            # ── Header ──────────────────────────────
            self._build_header(greeting, profile_name, date_str),
            sd_gap(Spacing.LG),

            # ── Overdue Warning ─────────────────────
            *(self._build_overdue_warning(overdue_tasks) if overdue_tasks else []),

            # ── Next Class ──────────────────────────
            sd_section_title(t("section_next_class")),
            sd_gap(Spacing.SM),
            self._build_next_class(next_class),
            sd_gap(Spacing.XL),

            # ── Today ───────────────────────────────
            sd_section_title(t("section_today_schedule")),
            sd_gap(Spacing.SM),
            self._build_today_summary(today_schedules, stats),
            sd_gap(Spacing.XL),

            # ── Urgent ──────────────────────────────
            *(self._build_urgent_section(urgent_tasks) if urgent_tasks else []),

            # ── Upcoming Deadlines ──────────────────
            sd_section_title(t("section_upcoming_deadlines")),
            sd_gap(Spacing.SM),
            self._build_upcoming(upcoming_tasks),
        ]

        return ft.Container(
            content=ft.Column(controls=sections, spacing=0, tight=True),
            padding=Spacing.PAGE_PADDING,
        )

    def _build_header(self, greeting: str, name: str, date_str: str) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Text(
                    f"{greeting}, {name}",
                    size=Typography.SIZE_PAGE_TITLE,
                    weight=ft.FontWeight.W_600,
                    color=Colors.TEXT,
                ),
                ft.Text(
                    date_str,
                    size=Typography.SIZE_BODY,
                    color=Colors.TEXT_MUTED,
                ),
            ],
            spacing=Spacing.XS,
            tight=True,
        )

    def _build_overdue_warning(self, overdue: list[Task]) -> list[ft.Control]:
        task_word = t("word_task_upper") if len(overdue) == 1 else t("word_tasks_upper")
        warning_text = t("overdue_warning_count", count=len(overdue), task_word=task_word)
        return [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=Colors.DANGER, size=16),
                        ft.Text(
                            warning_text,
                            size=Typography.SIZE_SMALL,
                            weight=ft.FontWeight.W_600,
                            color=Colors.DANGER,
                            expand=True,
                        ),
                        ft.TextButton(
                            t("btn_view"),
                            on_click=lambda _: self._on_navigate("tasks"),
                            style=ft.ButtonStyle(color=Colors.DANGER),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=Colors.DANGER_BG,
                padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
                border_radius=Radius.MD,
                border=ft.Border.all(1, Colors.DANGER),
            ),
            sd_gap(Spacing.LG),
        ]

    def _build_next_class(self, schedule: Schedule | None) -> ft.Control:
        if schedule is None:
            return sd_card(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY, color=Colors.BORDER, size=20),
                        sd_muted(t("no_upcoming_classes")),
                    ],
                    spacing=Spacing.SM,
                ),
                bgcolor=Colors.SURFACE,
            )

        TYPE_COLOR = {
            "Lecture": Colors.SCHEDULE_LECTURE,
            "Practicum": Colors.SCHEDULE_PRACTICUM,
            "Other": Colors.SCHEDULE_OTHER,
        }
        type_color = TYPE_COLOR.get(schedule.schedule_type.value, Colors.PRIMARY)

        now = now_local()
        course_name = schedule.course.name if schedule.course else t("unknown_course")
        start = schedule.start_time.strftime("%H:%M")
        end = schedule.end_time.strftime("%H:%M")
        room = schedule.room or "—"
        day_name = schedule.day_name

        sched_type_raw = schedule.schedule_type.value if hasattr(schedule.schedule_type, "value") else str(schedule.schedule_type)
        sched_type_label = t(f"schedule_type_{sched_type_raw.lower()}")

        return sd_card(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=4,
                        height=60,
                        bgcolor=type_color,
                        border_radius=Radius.PILL,
                    ),
                    ft.Container(width=Spacing.MD),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        course_name,
                                        size=Typography.SIZE_CARD_TITLE,
                                        weight=ft.FontWeight.W_600,
                                        color=Colors.TEXT,
                                        expand=True,
                                    ),
                                    sd_badge(
                                        sched_type_label,
                                        bgcolor=type_color,
                                        color=Colors.TEXT_ON_PRIMARY,
                                        small=True,
                                    ),
                                ],
                            ),
                            ft.Text(
                                f"{day_name} · {start} – {end}",
                                size=Typography.SIZE_BODY,
                                color=Colors.TEXT_MUTED,
                            ),
                            ft.Text(
                                f"📍 {room}",
                                size=Typography.SIZE_SMALL,
                                color=Colors.TEXT_MUTED,
                            ),
                        ],
                        spacing=Spacing.XS,
                        tight=True,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor=Colors.SURFACE_RAISED,
        )

    def _build_today_summary(self, today_schedules: list[Schedule], stats) -> ft.Control:
        n_classes = len(today_schedules)

        def _mini_stat(label: str, value: str, color: str = Colors.TEXT) -> ft.Container:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(value, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.W_600, color=color),
                        sd_caption(label),
                    ],
                    spacing=2,
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=Colors.SURFACE,
                padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
                border_radius=Radius.MD,
                border=ft.Border.all(1, Colors.BORDER_LIGHT),
                expand=True,
            )

        return ft.Row(
            controls=[
                _mini_stat(t("classes_today"), str(n_classes), Colors.PRIMARY),
                _mini_stat(t("active_tasks_count"), str(stats.active), Colors.PRIMARY_DARK),
                _mini_stat(t("overdue_count"), str(stats.overdue), Colors.DANGER if stats.overdue > 0 else Colors.TEXT_MUTED),
            ],
            spacing=Spacing.SM,
        )

    def _build_urgent_section(self, urgent: list[Task]) -> list[ft.Control]:
        return [
            sd_section_title(t("section_urgent")),
            sd_gap(Spacing.SM),
            ft.Column(
                controls=[self._build_task_row(t_item) for t_item in urgent[:3]],
                spacing=Spacing.SM,
                tight=True,
            ),
            sd_gap(Spacing.XL),
        ]

    def _build_upcoming(self, tasks: list[Task]) -> ft.Control:
        if not tasks:
            return sd_card(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=Colors.SUCCESS, size=18),
                        sd_muted(t("no_upcoming_deadlines_full")),
                    ],
                    spacing=Spacing.SM,
                ),
                bgcolor=Colors.SUCCESS_BG,
            )

        rows = [self._build_task_row(t) for t in tasks[:6]]
        controls: list[ft.Control] = []
        for row in rows:
            controls.append(row)

        return ft.Column(controls=controls, spacing=Spacing.SM, tight=True)

    def _build_task_row(self, task: Task) -> ft.Control:
        urgency = get_urgency_level(task.deadline)
        remaining = format_remaining(task.deadline)
        deadline_short = format_deadline(task.deadline)
        course_name = task.course.name if task.course else "—"

        URGENCY_TEXT_COLOR = {
            "overdue": Colors.DANGER,
            "critical": Colors.DANGER,
            "high": Colors.WARNING,
            "moderate": Colors.TEXT_MUTED,
            "normal": Colors.TEXT_MUTED,
            "none": Colors.TEXT_MUTED,
        }
        time_color = URGENCY_TEXT_COLOR.get(urgency, Colors.TEXT_MUTED)

        return sd_card(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                task.title,
                                size=Typography.SIZE_BODY,
                                weight=ft.FontWeight.W_600 if urgency in ("overdue", "critical") else ft.FontWeight.NORMAL,
                                color=Colors.TEXT,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            ),
                            ft.Row(
                                controls=[
                                    sd_caption(course_name),
                                    sd_caption("·"),
                                    ft.Text(remaining, size=Typography.SIZE_SMALL, color=time_color),
                                ],
                                spacing=Spacing.XS,
                                tight=True,
                            ),
                        ],
                        spacing=2,
                        tight=True,
                        expand=True,
                    ),
                    sd_priority_badge(task.priority.value, small=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=Colors.DANGER_BG if urgency == "overdue" else Colors.SURFACE_RAISED,
            border_color=Colors.DANGER if urgency == "overdue" else Colors.BORDER_LIGHT,
            on_click=lambda _, t=task: self._on_navigate(f"task_detail:{t.id}"),
            margin=None,
        )
