"""
Schedule page — weekly calendar and agenda view.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.schedule import Schedule, DayOfWeek
from src.services.schedule_service import ScheduleService
from src.ui.components.shared import (
    sd_card, sd_section_title, sd_body, sd_muted, sd_caption,
    sd_gap, sd_empty_state, sd_badge, sd_primary_button,
    safe_update,
)
from src.utils.datetime_utils import now_local
from src.utils.i18n import t


DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

TYPE_COLOR = {
    "Lecture": Colors.SCHEDULE_LECTURE,
    "Practicum": Colors.SCHEDULE_PRACTICUM,
    "Other": Colors.SCHEDULE_OTHER,
}


class SchedulePage(ft.Column):
    """Schedule page with weekly and agenda views."""

    def __init__(
        self,
        on_add_schedule: Callable,
        on_edit_schedule: Callable[[int], None],
    ) -> None:
        self._on_add = on_add_schedule
        self._on_edit = on_edit_schedule
        self._service = ScheduleService()
        self._view_mode = "week"  # "week" or "agenda"

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
        weekly = self._service.get_weekly()

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        t("schedule_title"),
                        size=Typography.SIZE_PAGE_TITLE,
                        weight=ft.FontWeight.W_600,
                        color=Colors.TEXT,
                        expand=True,
                    ),
                    ft.SegmentedButton(
                        selected=[self._view_mode],
                        segments=[
                            ft.Segment(value="week", label=ft.Text(t("view_week")), icon=ft.Icon(ft.Icons.GRID_VIEW)),
                            ft.Segment(value="agenda", label=ft.Text(t("view_agenda")), icon=ft.Icon(ft.Icons.VIEW_AGENDA)),
                        ],
                        on_change=self._on_view_change,
                    ),
                    ft.Container(width=Spacing.MD),
                    sd_primary_button(t("btn_add_schedule"), on_click=lambda _: self._on_add(), icon=ft.Icons.ADD),
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

        if self._view_mode == "week":
            content = self._build_weekly_view(weekly)
        else:
            content = self._build_agenda_view(weekly)

        return ft.Column(
            controls=[
                header,
                ft.Divider(height=1, color=Colors.BORDER_LIGHT),
                ft.Container(
                    content=content,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _on_view_change(self, e: ft.ControlEvent) -> None:
        selected = e.control.selected
        self._view_mode = next(iter(selected)) if selected else self._view_mode
        self.refresh()

    def _build_weekly_view(self, weekly: dict[int, list[Schedule]]) -> ft.Control:
        """7-column grid view with today highlighted."""
        today_dow = now_local().weekday()

        columns: list[ft.Control] = []
        for dow in range(7):
            is_today = dow == today_dow
            day_schedules = weekly.get(dow, [])

            day_header = ft.Container(
                content=ft.Text(
                    t(f"day_short_{dow}"),
                    size=Typography.SIZE_SMALL,
                    weight=ft.FontWeight.W_600,
                    color=Colors.TEXT_ON_PRIMARY if is_today else Colors.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=Colors.PRIMARY if is_today else "transparent",
                padding=ft.Padding.symmetric(vertical=Spacing.SM),
                border_radius=Radius.MD,
                width=100,
            )

            schedule_cells = [
                self._build_schedule_cell(s) for s in day_schedules
            ]

            columns.append(
                ft.Column(
                    controls=[
                        day_header,
                        sd_gap(Spacing.SM),
                        *schedule_cells,
                    ],
                    spacing=Spacing.XS,
                    tight=True,
                    width=100,
                )
            )

        return ft.Container(
            content=ft.Row(
                controls=columns,
                spacing=Spacing.SM,
                scroll=ft.ScrollMode.AUTO,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=Spacing.PAGE_PADDING,
            expand=True,
        )

    def _build_schedule_cell(self, schedule: Schedule) -> ft.Control:
        type_color = TYPE_COLOR.get(schedule.schedule_type.value, Colors.PRIMARY)
        course_name = schedule.course.name if schedule.course else "?"
        short_name = course_name if len(course_name) <= 12 else course_name[:10] + "…"

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        schedule.start_time.strftime("%H:%M"),
                        size=Typography.SIZE_CAPTION,
                        color=Colors.TEXT_MUTED,
                    ),
                    ft.Text(
                        short_name,
                        size=Typography.SIZE_SMALL,
                        weight=ft.FontWeight.W_600,
                        color=Colors.TEXT_ON_PRIMARY,
                        max_lines=2,
                    ),
                    ft.Text(
                        schedule.room or "—",
                        size=Typography.SIZE_CAPTION,
                        color=ft.Colors.with_opacity(0.8, Colors.TEXT_ON_PRIMARY),
                    ),
                ],
                spacing=2,
                tight=True,
            ),
            bgcolor=type_color,
            padding=Spacing.SM,
            border_radius=Radius.SM,
            width=100,
            on_click=lambda _, s=schedule: self._on_edit(s.id),
            ink=True,
        )

    def _build_agenda_view(self, weekly: dict[int, list[Schedule]]) -> ft.Control:
        """Chronological list starting from today."""
        today_dow = now_local().weekday()
        all_items: list[ft.Control] = []

        for offset in range(7):
            dow = (today_dow + offset) % 7
            schedules = weekly.get(dow, [])
            is_today = offset == 0

            day_label = ft.Container(
                content=ft.Text(
                    t("today_upper") if is_today else t(f"day_{dow}").upper(),
                    size=Typography.SIZE_SMALL,
                    weight=ft.FontWeight.W_600,
                    color=Colors.PRIMARY if is_today else Colors.TEXT_MUTED,
                    style=ft.TextStyle(letter_spacing=1.2),
                ),
                padding=ft.Padding.only(
                    left=Spacing.PAGE_PADDING,
                    top=Spacing.LG if offset > 0 else 0,
                    bottom=Spacing.SM,
                ),
            )
            all_items.append(day_label)

            if not schedules:
                all_items.append(
                    ft.Container(
                        content=sd_muted(t("no_classes_this_day")),
                        padding=ft.Padding.only(left=Spacing.PAGE_PADDING, bottom=Spacing.MD),
                    )
                )
            else:
                for s in schedules:
                    all_items.append(self._build_agenda_row(s))

        return ft.ListView(
            controls=all_items,
            spacing=0,
            padding=ft.Padding.only(bottom=Spacing.XXXL),
            expand=True,
        )

    def _build_agenda_row(self, schedule: Schedule) -> ft.Control:
        type_color = TYPE_COLOR.get(schedule.schedule_type.value, Colors.PRIMARY)
        course_name = schedule.course.name if schedule.course else t("unknown_course")
        sched_type_raw = schedule.schedule_type.value if hasattr(schedule.schedule_type, "value") else str(schedule.schedule_type)
        sched_type_label = t(f"schedule_type_{sched_type_raw.lower()}")

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            schedule.start_time.strftime("%H:%M"),
                            size=Typography.SIZE_SMALL,
                            color=Colors.TEXT_MUTED,
                            weight=ft.FontWeight.W_600,
                        ),
                        width=50,
                    ),
                    ft.Container(
                        width=3,
                        height=40,
                        bgcolor=type_color,
                        border_radius=Radius.PILL,
                    ),
                    ft.Container(width=Spacing.MD),
                    ft.Column(
                        controls=[
                            ft.Text(course_name, size=Typography.SIZE_BODY, weight=ft.FontWeight.W_600, color=Colors.TEXT),
                            ft.Row(
                                controls=[
                                    sd_badge(sched_type_label, bgcolor=type_color, color=Colors.TEXT_ON_PRIMARY, small=True),
                                    ft.Container(width=Spacing.XS),
                                    sd_caption(f"{schedule.start_time.strftime('%H:%M')} – {schedule.end_time.strftime('%H:%M')}"),
                                    *([ ft.Container(width=Spacing.XS), sd_caption(f"📍 {schedule.room}")] if schedule.room else []),
                                ],
                                spacing=0,
                                tight=True,
                            ),
                        ],
                        spacing=2,
                        tight=True,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        on_click=lambda _, s=schedule: self._on_edit(s.id),
                        icon_color=Colors.TEXT_MUTED,
                        icon_size=16,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.PAGE_PADDING, vertical=Spacing.MD),
            on_click=lambda _, s=schedule: self._on_edit(s.id),
            ink=True,
        )
