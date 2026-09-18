"""
Task detail page — comprehensive view for a single task.
Shows metadata, checklist with progress, attachments, reminders, and actions.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.task import Task, TaskStatus, Priority
from src.services.task_service import TaskService
from src.services.checklist_service import ChecklistService
from src.services.attachment_service import AttachmentService
from src.services.reminder_service import ReminderService
from src.ui.components.shared import (
    sd_card, sd_section_card, sd_badge, sd_priority_badge, sd_status_badge,
    sd_primary_button, sd_secondary_button, sd_danger_button, sd_icon_button,
    sd_text_field, sd_progress_bar, sd_empty_state, sd_gap, safe_update,
)
from src.ui.components.checklist_item import checklist_item_row
from src.ui.components.attachment_row import attachment_row
from src.utils.datetime_utils import format_deadline, format_remaining, is_overdue
from src.utils.i18n import t, translate_preset


class TaskDetailPage(ft.Column):
    """Full detail view for a specific task."""

    def __init__(
        self,
        task_id: int,
        on_back: Callable[[], None],
        on_edit: Callable[[int], None] | None = None,
        on_start_focus: Callable[[int], None] | None = None,
    ) -> None:
        self._task_id = task_id
        self._on_back = on_back
        self._on_edit = on_edit
        self._on_start_focus = on_start_focus

        self._task_service = TaskService()
        self._checklist_service = ChecklistService()
        self._attachment_service = AttachmentService()
        self._reminder_service = ReminderService()

        self._new_subtask_field = sd_text_field(
            label=t("label_add_subtask"),
            hint=t("hint_add_subtask"),
            expand=True,
        )

        super().__init__(
            controls=[],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=Spacing.LG,
            margin=Spacing.PAGE_PADDING,
        )
        self.refresh()

    def refresh(self) -> None:
        task = self._task_service.get_by_id(self._task_id)
        if not task:
            self.controls = [
                sd_empty_state(
                    icon=ft.Icons.ERROR_OUTLINE,
                    title=t("task_not_found"),
                    subtitle=t("task_not_found_sub"),
                    action=sd_primary_button(t("btn_go_back"), on_click=lambda _: self._on_back()),
                )
            ]
            safe_update(self)
            return

        self.controls = [
            self._build_top_bar(task),
            self._build_header_card(task),
            self._build_checklist_section(task),
            self._build_attachments_section(task),
            self._build_reminders_section(task),
        ]
        safe_update(self)

    def _build_top_bar(self, task: Task) -> ft.Row:
        actions: list[ft.Control] = []

        # Focus button
        if self._on_start_focus and task.status != TaskStatus.COMPLETED:
            actions.append(
                sd_secondary_button(
                    t("btn_focus"),
                    icon=ft.Icons.TIMER_OUTLINED,
                    on_click=lambda _: self._on_start_focus(task.id),
                )
            )

        # Toggle Complete
        is_done = task.status == TaskStatus.COMPLETED
        actions.append(
            sd_primary_button(
                t("btn_mark_done") if not is_done else t("btn_reopen"),
                icon=ft.Icons.CHECK_CIRCLE if not is_done else ft.Icons.REPLAY,
                on_click=lambda _: self._toggle_complete(),
            )
        )

        # Edit button
        if self._on_edit:
            actions.append(
                sd_icon_button(
                    icon=ft.Icons.EDIT_OUTLINED,
                    on_click=lambda _: self._on_edit(task.id),
                    tooltip=t("tooltip_edit_task"),
                    size=22,
                )
            )

        # Delete button
        actions.append(
            sd_icon_button(
                icon=ft.Icons.DELETE_OUTLINE,
                on_click=lambda _: self._confirm_delete(),
                tooltip=t("tooltip_delete_task"),
                color=Colors.DANGER,
                size=22,
            )
        )

        return ft.Row(
            controls=[
                sd_icon_button(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: self._on_back(),
                    tooltip=t("btn_back_to_tasks"),
                    size=24,
                ),
                ft.Text(
                    t("task_detail_title"),
                    size=Typography.SIZE_PAGE_TITLE,
                    weight=ft.FontWeight.W_600,
                    color=Colors.TEXT,
                    expand=True,
                ),
                ft.Row(controls=actions, spacing=Spacing.SM),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_header_card(self, task: Task) -> ft.Container:
        is_done = task.status == TaskStatus.COMPLETED
        overdue = is_overdue(task.deadline) and not is_done

        badges: list[ft.Control] = []
        if task.course:
            badges.append(
                sd_badge(
                    text=task.course.name,
                    bgcolor=task.course.color or Colors.PRIMARY,
                    color=Colors.TEXT_ON_PRIMARY,
                )
            )
        badges.append(sd_status_badge(task.status.value))
        badges.append(sd_priority_badge(task.priority.value))
        badges.append(
            sd_badge(
                text=task.task_type.value,
                bgcolor=Colors.SURFACE_INSET,
                color=Colors.TEXT,
            )
        )

        deadline_info = []
        if task.deadline:
            d_text = format_deadline(task.deadline)
            r_text = format_remaining(task.deadline)
            color = Colors.DANGER if overdue else Colors.TEXT_MUTED
            deadline_info.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ACCESS_TIME, size=16, color=color),
                        ft.Text(t("label_deadline", date=d_text, remaining=r_text), size=Typography.SIZE_BODY, color=color, weight=ft.FontWeight.W_600 if overdue else ft.FontWeight.NORMAL),
                    ],
                    spacing=Spacing.XS,
                )
            )

        if task.estimated_minutes:
            deadline_info.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.HOURGLASS_BOTTOM, size=16, color=Colors.TEXT_MUTED),
                        ft.Text(t("label_estimated_minutes", minutes=task.estimated_minutes), size=Typography.SIZE_BODY, color=Colors.TEXT_MUTED),
                    ],
                    spacing=Spacing.XS,
                )
            )

        return sd_card(
            content=ft.Column(
                controls=[
                    ft.Row(controls=badges, spacing=Spacing.SM, wrap=True),
                    ft.Text(
                        task.title,
                        size=Typography.SIZE_SECTION_TITLE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT,
                        decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE,
                    ),
                    *deadline_info,
                    *([ft.Divider(height=1, color=Colors.BORDER_LIGHT), ft.Text(task.description, size=Typography.SIZE_BODY, color=Colors.TEXT)] if task.description else []),
                ],
                spacing=Spacing.MD,
            )
        )

    def _build_checklist_section(self, task: Task) -> ft.Container:
        items = self._checklist_service.get_by_task(task.id)
        done_count, total_count = self._checklist_service.get_progress(task.id)

        rows: list[ft.Control] = []
        if total_count > 0:
            ratio = done_count / total_count
            progress_bar = sd_progress_bar(
                value=ratio,
                label=t("progress_label", done=done_count, total=total_count, pct=int(ratio * 100)),
                color=Colors.SUCCESS if ratio == 1.0 else Colors.PRIMARY,
            )
            rows.append(progress_bar)
            rows.append(sd_gap(Spacing.SM))

        for item in items:
            rows.append(
                checklist_item_row(
                    item=item,
                    on_toggle=self._handle_toggle_checklist,
                    on_delete=self._handle_delete_checklist,
                )
            )

        # Add subtask row
        def on_add_subtask(_: ft.ControlEvent) -> None:
            text = self._new_subtask_field.value.strip()
            if text:
                self._checklist_service.add_item(task.id, text)
                self._new_subtask_field.value = ""
                self.refresh()

        add_row = ft.Row(
            controls=[
                self._new_subtask_field,
                sd_primary_button(t("btn_add"), on_click=on_add_subtask),
            ],
            spacing=Spacing.SM,
        )
        rows.append(sd_gap(Spacing.SM))
        rows.append(add_row)

        done_label = t("label_subtasks", done=done_count, total=total_count) if total_count else t("label_subtasks_empty")
        return sd_section_card(
            title=done_label,
            content=ft.Column(controls=rows, spacing=Spacing.XS),
        )

    def _build_attachments_section(self, task: Task) -> ft.Container:
        attachments = self._attachment_service.get_by_task(task.id)

        rows: list[ft.Control] = []
        for att in attachments:
            rows.append(
                attachment_row(
                    attachment=att,
                    on_open=self._handle_open_attachment,
                    on_delete=self._handle_delete_attachment,
                )
            )

        if not attachments:
            rows.append(
                ft.Text(t("no_attachments"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED)
            )

        # File picker button
        file_picker = ft.FilePicker(on_result=self._handle_file_picked)
        if self.page and file_picker not in self.page.overlay:
            self.page.overlay.append(file_picker)

        upload_btn = sd_secondary_button(
            t("btn_attach_file"),
            icon=ft.Icons.ATTACH_FILE,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False),
        )

        return sd_section_card(
            title=t("label_attachments", count=len(attachments)),
            title_action=upload_btn,
            content=ft.Column(controls=rows, spacing=Spacing.SM),
        )

    def _build_reminders_section(self, task: Task) -> ft.Container:
        reminders = self._reminder_service.get_by_task(task.id)

        rows: list[ft.Control] = []
        for rem in reminders:
            status_color = Colors.SUCCESS if rem.is_sent else (Colors.DANGER if rem.is_missed else Colors.PRIMARY)
            status_text = t("reminder_sent") if rem.is_sent else (t("reminder_missed") if rem.is_missed else t("reminder_scheduled"))
            rem_time = rem.remind_at.strftime("%d %b %Y, %H:%M") if rem.remind_at else "—"

            rows.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=18, color=status_color),
                            ft.Text(f"{translate_preset(rem.preset_label)}: {rem_time}", size=Typography.SIZE_BODY, color=Colors.TEXT, expand=True),
                            sd_badge(status_text, bgcolor=status_color, small=True),
                            sd_icon_button(
                                icon=ft.Icons.CLOSE,
                                on_click=lambda _, r_id=rem.id: self._handle_delete_reminder(r_id),
                                size=16,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=Spacing.SM,
                    ),
                    padding=Spacing.SM,
                    bgcolor=Colors.SURFACE_INSET,
                    border_radius=Radius.SM,
                )
            )

        if not reminders:
            rows.append(
                ft.Text(t("no_reminders"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED)
            )

        return sd_section_card(
            title=t("label_reminders_count", count=len(reminders)),
            content=ft.Column(controls=rows, spacing=Spacing.SM),
        )

    def _toggle_complete(self) -> None:
        self._task_service.toggle_complete(self._task_id)
        self.refresh()

    def _confirm_delete(self) -> None:
        def do_delete(_: ft.ControlEvent) -> None:
            dialog.open = False
            if self.page:
                self.page.update()
            self._task_service.delete(self._task_id)
            self._on_back()

        dialog = ft.AlertDialog(
            title=ft.Text(t("dlg_delete_task_title")),
            content=ft.Text(t("dlg_delete_task_body")),
            actions=[
                sd_secondary_button(t("btn_cancel"), on_click=lambda _: self._close_dialog(dialog)),
                sd_danger_button(t("btn_delete"), on_click=do_delete),
            ],
            modal=True,
        )
        if self.page:
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False
        if self.page:
            self.page.update()

    def _handle_toggle_checklist(self, item_id: int) -> None:
        self._checklist_service.toggle_item(item_id)
        self.refresh()

    def _handle_delete_checklist(self, item_id: int) -> None:
        self._checklist_service.delete_item(item_id)
        self.refresh()

    def _handle_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.files and len(e.files) > 0:
            picked_path = e.files[0].path
            if picked_path:
                self._attachment_service.add_attachment(self._task_id, picked_path)
                self.refresh()

    def _handle_open_attachment(self, attachment_id: int) -> None:
        self._attachment_service.open_attachment(attachment_id)

    def _handle_delete_attachment(self, attachment_id: int) -> None:
        self._attachment_service.remove_attachment(attachment_id)
        self.refresh()

    def _handle_delete_reminder(self, reminder_id: int) -> None:
        self._reminder_service.delete(reminder_id)
        self.refresh()
