"""
Settings page — profile, semester, courses management, preferences, and database backup/export.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography, REMINDER_PRESETS, APP_NAME, APP_VERSION
from src.database.connection import get_db
from src.database.models.semester import Semester
from src.database.repositories.semester_repository import SemesterRepository
from src.services.settings_service import SettingsService
from src.services.course_service import CourseService
from src.services.backup_service import BackupService
from src.ui.dialogs.course_dialog import CourseDialog
from src.ui.components.shared import (
    sd_card, sd_section_card, sd_primary_button, sd_secondary_button,
    sd_danger_button, sd_icon_button, sd_text_field, sd_dropdown,
    sd_badge, sd_success_banner, sd_error_banner, sd_gap, safe_update,
)
from src.utils.i18n import t, translate_preset, set_language, get_language


class SettingsPage(ft.Column):
    """Application settings, academic profile, course catalog, and data backup."""

    def __init__(
        self,
        on_course_updated: Callable[[], None] | None = None,
        on_language_changed: Callable[[str], None] | None = None,
    ) -> None:
        self._on_course_updated = on_course_updated
        self._on_language_changed = on_language_changed
        self._settings_service = SettingsService()
        self._course_service = CourseService()
        self._backup_service = BackupService()

        # Feedback banner
        self._feedback_container = ft.Column(tight=True)

        super().__init__(
            controls=[],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=Spacing.LG,
            margin=Spacing.PAGE_PADDING,
        )
        self.refresh()

    def refresh(self) -> None:
        self.controls = [
            ft.Text(t("settings_title"), size=Typography.SIZE_PAGE_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
            self._feedback_container,
            self._build_profile_section(),
            self._build_language_section(),
            self._build_semester_section(),
            self._build_courses_section(),
            self._build_preferences_section(),
            self._build_backup_section(),
            self._build_about_section(),
        ]
        safe_update(self)

    def _build_language_section(self) -> ft.Container:
        current_lang = self._settings_service.get_language()

        def on_lang_change(e: ft.ControlEvent) -> None:
            if e.control.value:
                new_lang = e.control.value
                self._settings_service.set_language(new_lang)
                msg = (
                    "Bahasa berhasil diubah ke Bahasa Indonesia."
                    if new_lang == "id"
                    else "Language switched to English."
                )
                self._show_message(msg)
                if self._on_language_changed:
                    self._on_language_changed(new_lang)
                self.refresh()

        options = [
            ft.dropdown.Option(key="id", text=t("lang_id")),
            ft.dropdown.Option(key="en", text=t("lang_en")),
        ]
        dropdown = sd_dropdown(
            label=t("language_label"),
            options=options,
            value=current_lang,
            on_change=on_lang_change,
            expand=True,
        )

        return sd_section_card(
            title=t("language_section").upper(),
            content=ft.Row(
                controls=[dropdown],
                spacing=Spacing.MD,
            ),
        )

    def _show_message(self, message: str, is_error: bool = False) -> None:
        banner = sd_error_banner(message) if is_error else sd_success_banner(message)
        self._feedback_container.controls = [banner, sd_gap(Spacing.SM)]
        self._feedback_container.update()

    def _build_profile_section(self) -> ft.Container:
        current_name = self._settings_service.get_profile_name()
        name_field = sd_text_field(
            label=t("field_profile_name"),
            value=current_name,
            hint=t("hint_profile_name"),
            expand=True,
        )

        def save_profile(_: ft.ControlEvent) -> None:
            if name_field.value.strip():
                self._settings_service.set_profile_name(name_field.value.strip())
                self._show_message(t("msg_profile_updated"))

        return sd_section_card(
            title=t("section_profile"),
            content=ft.Row(
                controls=[
                    name_field,
                    sd_primary_button(t("btn_save"), on_click=save_profile),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.MD,
            ),
        )

    def _build_semester_section(self) -> ft.Container:
        active_id = self._settings_service.get_active_semester_id()

        semesters: list[Semester] = []
        try:
            with get_db() as session:
                repo = SemesterRepository(session)
                semesters = repo.get_all()
        except Exception:
            pass

        options = [
            ft.dropdown.Option(key=str(s.id), text=f"{s.name} ({s.academic_year})")
            for s in semesters
        ]

        def on_semester_change(e: ft.ControlEvent) -> None:
            if e.control.value:
                self._settings_service.set_active_semester_id(int(e.control.value))
                try:
                    with get_db() as session:
                        repo = SemesterRepository(session)
                        repo.set_active(int(e.control.value))
                except Exception:
                    pass
                self._show_message(t("msg_semester_updated"))

        dropdown = sd_dropdown(
            label=t("field_active_semester"),
            options=options,
            value=str(active_id) if active_id else (options[0].key if options else None),
            on_change=on_semester_change,
            expand=True,
        )

        def show_add_semester(_: ft.ControlEvent) -> None:
            self._show_add_semester_dialog()

        return sd_section_card(
            title=t("section_semester"),
            title_action=sd_secondary_button(t("btn_new_semester"), on_click=show_add_semester),
            content=ft.Row(
                controls=[dropdown],
                spacing=Spacing.MD,
            ),
        )

    def _show_add_semester_dialog(self) -> None:
        name_in = sd_text_field(label=t("field_semester_name"), hint=t("hint_semester_name"))
        year_in = sd_text_field(label=t("field_academic_year"), hint=t("hint_academic_year"))
        active_chk = ft.Checkbox(label=t("checkbox_set_active"), value=True)
        err_col = ft.Column(tight=True)

        def save_sem(_: ft.ControlEvent) -> None:
            if not name_in.value.strip() or not year_in.value.strip():
                err_col.controls = [sd_error_banner(t("err_semester_required"))]
                err_col.update()
                return

            try:
                with get_db() as session:
                    repo = SemesterRepository(session)
                    sem = Semester(
                        name=name_in.value.strip(),
                        academic_year=year_in.value.strip(),
                        is_active=active_chk.value,
                    )
                    repo.add(sem)
                    if active_chk.value:
                        repo.set_active(sem.id)
                        self._settings_service.set_active_semester_id(sem.id)

                dlg.open = False
                if self.page:
                    self.page.update()
                self._show_message(t("msg_semester_added"))
                self.refresh()
            except Exception as e:
                err_col.controls = [sd_error_banner(str(e))]
                err_col.update()

        dlg = ft.AlertDialog(
            title=ft.Text(t("dlg_add_semester")),
            content=ft.Container(
                content=ft.Column(
                    controls=[err_col, name_in, year_in, active_chk],
                    spacing=Spacing.MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                sd_secondary_button(t("btn_cancel"), on_click=lambda _: self._close_dlg(dlg)),
                sd_primary_button(t("btn_create"), on_click=save_sem),
            ],
            modal=True,
        )
        if self.page:
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

    def _build_courses_section(self) -> ft.Container:
        courses = self._course_service.get_all()

        course_rows: list[ft.Control] = []
        for c in courses:
            c_color = c.color or Colors.PRIMARY
            code_badge = sd_badge(c.code, bgcolor=Colors.SURFACE_INSET, color=Colors.TEXT, small=True) if c.code else ft.Container()
            course_rows.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(width=12, height=12, border_radius=Radius.PILL, bgcolor=c_color),
                            ft.Text(c.name, size=Typography.SIZE_BODY, weight=ft.FontWeight.W_600, color=Colors.TEXT, expand=True),
                            code_badge,
                            sd_icon_button(
                                icon=ft.Icons.EDIT_OUTLINED,
                                on_click=lambda _, course_obj=c: self._open_edit_course(course_obj),
                                tooltip=t("tooltip_edit_course"),
                                size=18,
                            ),
                            sd_icon_button(
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda _, course_id=c.id: self._confirm_delete_course(course_id),
                                tooltip=t("tooltip_delete_course"),
                                color=Colors.DANGER,
                                size=18,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=Spacing.MD,
                    ),
                    padding=Spacing.SM,
                    bgcolor=Colors.SURFACE_INSET,
                    border_radius=Radius.SM,
                )
            )

        if not courses:
            course_rows.append(
                ft.Text(t("no_courses_yet"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED)
            )

        return sd_section_card(
            title=t("section_courses", count=len(courses)),
            title_action=sd_primary_button(t("btn_add_course_action"), on_click=lambda _: self._open_add_course()),
            content=ft.Column(controls=course_rows, spacing=Spacing.SM),
        )

    def _open_add_course(self) -> None:
        def on_saved(_) -> None:
            self._show_message(t("msg_course_added"))
            self.refresh()
            if self._on_course_updated:
                self._on_course_updated()

        dlg = CourseDialog(course=None, on_saved=on_saved)
        if self.page:
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

    def _open_edit_course(self, course) -> None:
        def on_saved(_) -> None:
            self._show_message(t("msg_course_updated"))
            self.refresh()
            if self._on_course_updated:
                self._on_course_updated()

        dlg = CourseDialog(course=course, on_saved=on_saved)
        if self.page:
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

    def _confirm_delete_course(self, course_id: int) -> None:
        def do_delete(_: ft.ControlEvent) -> None:
            dlg.open = False
            if self.page:
                self.page.update()
            success, msg = self._course_service.delete(course_id)
            if success:
                self._show_message(t("msg_course_deleted"))
                self.refresh()
                if self._on_course_updated:
                    self._on_course_updated()
            else:
                self._show_message(msg, is_error=True)

        dlg = ft.AlertDialog(
            title=ft.Text(t("dlg_delete_course_title")),
            content=ft.Text(t("dlg_delete_course_body")),
            actions=[
                sd_secondary_button(t("btn_cancel"), on_click=lambda _: self._close_dlg(dlg)),
                sd_danger_button(t("btn_delete"), on_click=do_delete),
            ],
            modal=True,
        )
        if self.page:
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

    def _build_preferences_section(self) -> ft.Container:
        reminder_options = [
            ft.dropdown.Option(key=label, text=translate_preset(label))
            for label in REMINDER_PRESETS.keys()
            if label != "Custom"
        ]
        cur_rem = self._settings_service.get_default_reminder()

        def on_rem_change(e: ft.ControlEvent) -> None:
            if e.control.value:
                self._settings_service.set_default_reminder(e.control.value)
                self._show_message(t("msg_profile_updated"))

        rem_dropdown = sd_dropdown(
            label=t("field_default_reminder"),
            options=reminder_options,
            value=cur_rem,
            on_change=on_rem_change,
            expand=True,
        )

        notif_switch = ft.Switch(
            label=t("switch_notifications"),
            value=self._settings_service.get_notifications_enabled(),
            on_change=lambda e: self._settings_service.set_notifications_enabled(e.control.value),
            active_color=Colors.PRIMARY,
        )

        return sd_section_card(
            title=t("section_preferences"),
            content=ft.Column(
                controls=[
                    rem_dropdown,
                    notif_switch,
                ],
                spacing=Spacing.MD,
            ),
        )

    def _build_backup_section(self) -> ft.Container:
        def do_backup(_: ft.ControlEvent) -> None:
            dest, err = self._backup_service.backup_database()
            if dest:
                self._show_message(t("msg_backup_done", name=dest.name))
            else:
                self._show_message(err, is_error=True)

        def do_export_csv(_: ft.ControlEvent) -> None:
            dest, err = self._backup_service.export_tasks_csv()
            if dest:
                self._show_message(t("msg_export_csv_done", name=dest.name))
            else:
                self._show_message(err, is_error=True)

        def do_export_json(_: ft.ControlEvent) -> None:
            dest, err = self._backup_service.export_tasks_json()
            if dest:
                self._show_message(t("msg_export_json_done", name=dest.name))
            else:
                self._show_message(err, is_error=True)

        return sd_section_card(
            title=t("section_backup"),
            content=ft.Column(
                controls=[
                    ft.Text(t("backup_description"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                    ft.Row(
                        controls=[
                            sd_primary_button(t("btn_backup_db"), icon=ft.Icons.BACKUP, on_click=do_backup),
                            sd_secondary_button(t("btn_export_csv"), icon=ft.Icons.DOWNLOAD, on_click=do_export_csv),
                            sd_secondary_button(t("btn_export_json"), icon=ft.Icons.CODE, on_click=do_export_json),
                        ],
                        spacing=Spacing.MD,
                        wrap=True,
                    ),
                ],
                spacing=Spacing.MD,
            ),
        )

    def _build_about_section(self) -> ft.Container:
        return sd_card(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=Colors.PRIMARY, size=20),
                    ft.Text(t("about_text", app=APP_NAME, ver=APP_VERSION), size=Typography.SIZE_CAPTION, color=Colors.TEXT_MUTED, expand=True),
                ],
                spacing=Spacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=Colors.SURFACE_INSET,
            border_color=Colors.BORDER_LIGHT,
        )

    def _close_dlg(self, dlg: ft.AlertDialog) -> None:
        dlg.open = False
        if self.page:
            self.page.update()
