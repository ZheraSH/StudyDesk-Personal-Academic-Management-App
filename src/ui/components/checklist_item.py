"""
Checklist item component — subtask row with checkbox, strikethrough, and delete button.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Typography
from src.database.models.task_checklist import TaskChecklist
from src.ui.components.shared import sd_icon_button
from src.utils.i18n import t


def checklist_item_row(
    item: TaskChecklist,
    on_toggle: Callable[[int], None],
    on_delete: Callable[[int], None] | None = None,
) -> ft.Container:
    """A single subtask row inside task details."""
    title_text = ft.Text(
        item.title,
        size=Typography.SIZE_BODY,
        color=Colors.TEXT_MUTED if item.is_completed else Colors.TEXT,
        decoration=ft.TextDecoration.LINE_THROUGH if item.is_completed else ft.TextDecoration.NONE,
        expand=True,
    )

    checkbox = ft.Checkbox(
        value=item.is_completed,
        on_change=lambda _: on_toggle(item.id),
        fill_color={
            ft.ControlState.SELECTED: Colors.SUCCESS,
            ft.ControlState.DEFAULT: Colors.BORDER,
        },
        check_color=Colors.TEXT_ON_PRIMARY,
    )

    delete_btn = (
        sd_icon_button(
            icon=ft.Icons.CLOSE,
            on_click=lambda _: on_delete(item.id),
            tooltip=t("tooltip_delete_subtask"),
            color=Colors.TEXT_DISABLED,
            size=16,
        )
        if on_delete
        else ft.Container()
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                checkbox,
                title_text,
                delete_btn,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.SM,
        ),
        padding=ft.Padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.XS),
    )
