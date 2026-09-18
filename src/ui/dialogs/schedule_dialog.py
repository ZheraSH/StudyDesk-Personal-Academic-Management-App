"""
Schedule dialog — modal for adding or editing a weekly schedule entry.
"""
from __future__ import annotations
from datetime import time
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.schedule import Schedule, ScheduleType, DayOfWeek
from src.services.schedule_service import ScheduleService, ScheduleData
from src.services.course_service import CourseService
from src.utils.i18n import t
from src.ui.components.shared import (
    sd_text_field, sd_dropdown, sd_primary_button, sd_secondary_button,
    sd_error_banner, sd_gap,
)


def _day_options() -> list[ft.dropdown.Option]:
    return [
        ft.dropdown.Option(key=str(i), text=t(f"day_{i}"))
        for i in range(7)
    ]


class ScheduleDialog(ft.AlertDialog):
    """Modal dialog for creating or editing a schedule block."""

    def __init__(
        self,
        schedule: Schedule | None = None,
        on_saved: Callable[[Schedule], None] | None = None,
    ) -> None:
        self._schedule = schedule
        self._on_saved = on_saved
        self._service = ScheduleService()
        self._course_service = CourseService()

        # Courses
        courses = self._course_service.get_all()
        course_options = [
            ft.dropdown.Option(
                key=str(c.id),
                text=f"{c.code + ' - ' if c.code else ''}{c.name}",
            )
            for c in courses
        ]

        selected_course = str(schedule.course_id) if schedule else (course_options[0].key if course_options else None)

        self._course_dropdown = sd_dropdown(
            label=t("field_course_required"),
            options=course_options,
            value=selected_course,
            expand=True,
        )

        # Type
        type_options = [
            ft.dropdown.Option(key=st.value, text=t(f"schedule_type_{st.value.lower()}"))
            for st in ScheduleType
        ]
        selected_type = schedule.schedule_type.value if schedule else ScheduleType.LECTURE.value
        self._type_dropdown = sd_dropdown(
            label=t("field_type"),
            options=type_options,
            value=selected_type,
            expand=True,
        )

        # Day of week (localized)
        self._day_dropdown = sd_dropdown(
            label=t("field_day"),
            options=_day_options(),
            value=str(schedule.day_of_week) if schedule else "0",
            expand=True,
        )

        # Start and end times
        st_val = schedule.start_time.strftime("%H:%M") if schedule else "08:00"
        et_val = schedule.end_time.strftime("%H:%M") if schedule else "09:40"

        self._start_time_field = sd_text_field(
            label=t("field_start_time"),
            value=st_val,
            hint="08:00",
            expand=True,
        )
        self._end_time_field = sd_text_field(
            label=t("field_end_time"),
            value=et_val,
            hint="09:40",
            expand=True,
        )

        # Room & Notes
        self._room_field = sd_text_field(
            label=t("field_room"),
            value=schedule.room if schedule and schedule.room else "",
            hint=t("hint_room"),
        )
        self._notes_field = sd_text_field(
            label=t("field_notes"),
            value=schedule.notes if schedule and schedule.notes else "",
            hint=t("hint_notes"),
            multiline=True,
            max_lines=2,
        )

        self._error_container = ft.Column(tight=True)

        content = ft.Container(
            content=ft.Column(
                controls=[
                    self._error_container,
                    self._course_dropdown,
                    ft.Row(
                        controls=[self._type_dropdown, self._day_dropdown],
                        spacing=Spacing.MD,
                    ),
                    ft.Row(
                        controls=[self._start_time_field, self._end_time_field],
                        spacing=Spacing.MD,
                    ),
                    self._room_field,
                    self._notes_field,
                ],
                spacing=Spacing.MD,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=500,
            padding=Spacing.MD,
        )

        title_text = t("dlg_edit_schedule") if schedule else t("dlg_add_schedule")

        super().__init__(
            modal=True,
            title=ft.Text(title_text, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
            content=content,
            actions=[
                sd_secondary_button(t("btn_cancel"), on_click=self._close_dialog),
                sd_primary_button(t("btn_save_schedule"), on_click=self._save_schedule),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=Radius.LG),
            bgcolor=Colors.SURFACE_RAISED,
        )

    def _close_dialog(self, _: ft.ControlEvent | None = None) -> None:
        self.open = False
        if self.page:
            self.page.update()

    def _parse_time(self, raw: str) -> time | None:
        parts = raw.strip().split(":")
        if len(parts) != 2:
            return None
        try:
            h = int(parts[0])
            m = int(parts[1])
            if 0 <= h < 24 and 0 <= m < 60:
                return time(h, m)
        except ValueError:
            pass
        return None

    def _save_schedule(self, _: ft.ControlEvent) -> None:
        if not self._course_dropdown.value:
            self._show_error(t("err_select_course"))
            return

        start_t = self._parse_time(self._start_time_field.value)
        if not start_t:
            self._show_error(t("err_invalid_start_time"))
            return

        end_t = self._parse_time(self._end_time_field.value)
        if not end_t:
            self._show_error(t("err_invalid_end_time"))
            return

        if start_t >= end_t:
            self._show_error(t("err_start_before_end"))
            return

        course_id = int(self._course_dropdown.value)
        day_of_week = int(self._day_dropdown.value)
        st_enum = ScheduleType(self._type_dropdown.value)

        data = ScheduleData(
            course_id=course_id,
            day_of_week=day_of_week,
            start_time=start_t,
            end_time=end_t,
            schedule_type=st_enum,
            room=self._room_field.value.strip(),
            notes=self._notes_field.value.strip(),
        )

        if self._schedule:
            saved, errors = self._service.update(self._schedule.id, data)
        else:
            saved, errors = self._service.create(data)

        if errors:
            self._show_error(errors[0])
            return

        self._close_dialog()
        if self._on_saved and saved:
            self._on_saved(saved)

    def _show_error(self, message: str) -> None:
        self._error_container.controls = [sd_error_banner(message), sd_gap(Spacing.SM)]
        self._error_container.update()
