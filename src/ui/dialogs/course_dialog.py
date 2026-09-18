"""
Course dialog — modal for adding or editing a university course.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.course import Course
from src.services.course_service import CourseService, CourseData
from src.services.settings_service import SettingsService
from src.database.repositories.semester_repository import SemesterRepository
from src.database.connection import get_db
from src.utils.i18n import t
from src.ui.components.shared import (
    sd_text_field, sd_dropdown, sd_primary_button, sd_secondary_button,
    sd_error_banner, sd_gap,
)

PRESET_COLORS = [
    "#6F5A8E",  # Royal Purple (default)
    "#5E7A9E",  # Slate Blue
    "#748A77",  # Sage Green
    "#AD8E61",  # Warm Amber
    "#A66F78",  # Rose
    "#4A7C7D",  # Muted Teal
    "#8E6F5A",  # Warm Taupe
    "#7B68EE",  # Medium Slate
]


class CourseDialog(ft.AlertDialog):
    """Modal dialog for creating or updating a course."""

    def __init__(
        self,
        course: Course | None = None,
        on_saved: Callable[[Course], None] | None = None,
    ) -> None:
        self._course = course
        self._on_saved = on_saved
        self._service = CourseService()
        self._selected_color = course.color if course and course.color else PRESET_COLORS[0]

        # Form fields
        self._name_field = sd_text_field(
            label=t("field_course_name"),
            value=course.name if course else "",
            hint=t("hint_course_name"),
            autofocus=True,
        )
        self._code_field = sd_text_field(
            label=t("field_course_code"),
            value=course.code if course and course.code else "",
            hint=t("hint_course_code"),
        )
        self._lecturer_field = sd_text_field(
            label=t("field_lecturer"),
            value=course.lecturer if course and course.lecturer else "",
            hint=t("hint_lecturer"),
        )
        self._room_field = sd_text_field(
            label=t("field_default_room"),
            value=course.room if course and course.room else "",
            hint=t("hint_default_room"),
        )
        self._notes_field = sd_text_field(
            label=t("field_course_notes"),
            value=course.notes if course and course.notes else "",
            hint=t("hint_course_notes"),
            multiline=True,
            max_lines=3,
        )

        # Semester dropdown
        self._semester_options = self._load_semesters()
        current_sem_id = str(course.semester_id) if (course and course.semester_id) else None
        if not current_sem_id and self._semester_options:
            current_sem_id = self._semester_options[0].key

        self._semester_dropdown = sd_dropdown(
            label=t("field_semester"),
            options=self._semester_options,
            value=current_sem_id,
        )

        self._error_container = ft.Column(tight=True)
        self._color_swatches = self._build_color_swatches()

        content = ft.Container(
            content=ft.Column(
                controls=[
                    self._error_container,
                    self._name_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=self._code_field, expand=1),
                            ft.Container(content=self._semester_dropdown, expand=1),
                        ],
                        spacing=Spacing.MD,
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(content=self._lecturer_field, expand=1),
                            ft.Container(content=self._room_field, expand=1),
                        ],
                        spacing=Spacing.MD,
                    ),
                    ft.Text(t("label_course_color"), size=Typography.SIZE_SMALL, weight=ft.FontWeight.W_600, color=Colors.TEXT_MUTED),
                    self._color_swatches,
                    self._notes_field,
                ],
                spacing=Spacing.MD,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=500,
            padding=Spacing.MD,
        )

        title_text = t("dlg_edit_course") if course else t("dlg_add_course")

        super().__init__(
            modal=True,
            title=ft.Text(title_text, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
            content=content,
            actions=[
                sd_secondary_button(t("btn_cancel"), on_click=self._close_dialog),
                sd_primary_button(t("btn_save_course"), on_click=self._save_course),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=Radius.LG),
            bgcolor=Colors.SURFACE_RAISED,
        )

    def _load_semesters(self) -> list[ft.dropdown.Option]:
        try:
            with get_db() as session:
                repo = SemesterRepository(session)
                semesters = repo.get_all()
                return [ft.dropdown.Option(key=str(s.id), text=f"{s.name} ({s.academic_year})") for s in semesters]
        except Exception:
            return []

    def _build_color_swatches(self) -> ft.Row:
        swatches: list[ft.Control] = []
        for color_hex in PRESET_COLORS:
            is_selected = color_hex.lower() == self._selected_color.lower()

            def make_click(c: str) -> Callable:
                return lambda _: self._select_color(c)

            swatches.append(
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=Radius.PILL,
                    bgcolor=color_hex,
                    border=ft.Border.all(3, Colors.PRIMARY_DARK) if is_selected else ft.Border.all(1, Colors.BORDER_LIGHT),
                    content=ft.Icon(ft.Icons.CHECK, size=16, color=Colors.TEXT_ON_PRIMARY) if is_selected else None,
                    on_click=make_click(color_hex),
                    ink=True,
                )
            )
        return ft.Row(controls=swatches, spacing=Spacing.SM)

    def _select_color(self, color_hex: str) -> None:
        self._selected_color = color_hex
        self._color_swatches.controls = self._build_color_swatches().controls
        self._color_swatches.update()

    def _close_dialog(self, _: ft.ControlEvent | None = None) -> None:
        self.open = False
        if self.page:
            self.page.update()

    def _save_course(self, _: ft.ControlEvent) -> None:
        name = self._name_field.value.strip()
        if not name:
            self._show_error(t("err_course_name_required"))
            return

        sem_id = int(self._semester_dropdown.value) if self._semester_dropdown.value else None

        data = CourseData(
            name=name,
            code=self._code_field.value.strip(),
            lecturer=self._lecturer_field.value.strip(),
            room=self._room_field.value.strip(),
            color=self._selected_color,
            notes=self._notes_field.value.strip(),
            semester_id=sem_id,
        )

        if self._course:
            course, errors = self._service.update(self._course.id, data)
        else:
            course, errors = self._service.create(data)

        if errors:
            self._show_error(errors[0])
            return

        self._close_dialog()
        if self._on_saved and course:
            self._on_saved(course)

    def _show_error(self, message: str) -> None:
        self._error_container.controls = [sd_error_banner(message), sd_gap(Spacing.SM)]
        self._error_container.update()
