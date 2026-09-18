"""
Task card component — interactive card showing title, course, deadline, priority, and completion status.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.task import Task, TaskStatus, Priority
from src.ui.components.shared import (
    sd_badge, sd_priority_badge, sd_status_badge, sd_icon_button
)
from src.utils.datetime_utils import format_deadline, format_remaining, is_overdue, get_urgency_level
from src.utils.i18n import t

PRIORITY_BORDER_COLORS = {
    Priority.URGENT: Colors.PRIORITY_URGENT,
    Priority.HIGH: Colors.PRIORITY_HIGH,
    Priority.MEDIUM: Colors.BORDER_LIGHT,
    Priority.LOW: Colors.BORDER_LIGHT,
}


def task_card(
    task: Task,
    on_click: Callable[[int], None] | None = None,
    on_toggle_complete: Callable[[int], None] | None = None,
    on_edit: Callable[[int], None] | None = None,
    on_delete: Callable[[int], None] | None = None,
) -> ft.Container:
    """Card for displaying a single task in list views."""
    is_done = task.status == TaskStatus.COMPLETED
    overdue = is_overdue(task.deadline) and not is_done

    # Deadline label
    if task.deadline:
        deadline_text = format_deadline(task.deadline)
        rem_text = format_remaining(task.deadline)
        if overdue:
            deadline_color = Colors.DANGER
            deadline_icon = ft.Icons.ERROR_OUTLINE
        else:
            deadline_color = Colors.TEXT_MUTED
            deadline_icon = ft.Icons.ACCESS_TIME
    else:
        deadline_text = t("no_deadline")
        rem_text = ""
        deadline_color = Colors.TEXT_DISABLED
        deadline_icon = ft.Icons.EVENT_NOTE

    # Course info
    course_name = task.course.name if task.course else None
    course_color = getattr(task.course, "color", Colors.PRIMARY) if task.course else Colors.PRIMARY

    # Title styling
    title_text = ft.Text(
        task.title,
        size=Typography.SIZE_BODY_LARGE,
        weight=ft.FontWeight.W_600,
        color=Colors.TEXT_MUTED if is_done else Colors.TEXT,
        decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
        expand=True,
    )

    # Checkbox
    def handle_check(e: ft.ControlEvent) -> None:
        if on_toggle_complete:
            on_toggle_complete(task.id)

    checkbox = ft.Checkbox(
        value=is_done,
        on_change=handle_check,
        fill_color={
            ft.ControlState.SELECTED: Colors.SUCCESS,
            ft.ControlState.DEFAULT: Colors.BORDER,
        },
        check_color=Colors.TEXT_ON_PRIMARY,
    )

    # Badges row
    badges: list[ft.Control] = []
    if course_name:
        badges.append(
            sd_badge(
                text=course_name if len(course_name) <= 15 else course_name[:13] + "…",
                bgcolor=course_color,
                color=Colors.TEXT_ON_PRIMARY,
                small=True,
            )
        )

    task_type_raw = task.task_type.value if hasattr(task.task_type, "value") else str(task.task_type)
    task_type_label = t(f"task_type_{task_type_raw.lower()}")

    badges.append(
        sd_badge(
            text=task_type_label,
            bgcolor=Colors.SURFACE_INSET,
            color=Colors.TEXT_MUTED,
            small=True,
        )
    )

    badges.append(
        sd_priority_badge(
            priority=task.priority.value if hasattr(task.priority, "value") else str(task.priority),
            small=True,
        )
    )

    # Action buttons
    action_controls: list[ft.Control] = []
    if on_edit:
        action_controls.append(
            sd_icon_button(
                icon=ft.Icons.EDIT_OUTLINED,
                on_click=lambda _: on_edit(task.id),
                tooltip=t("tooltip_edit_task"),
                size=18,
            )
        )
    if on_delete:
        action_controls.append(
            sd_icon_button(
                icon=ft.Icons.DELETE_OUTLINE,
                on_click=lambda _: on_delete(task.id),
                tooltip=t("tooltip_delete_task"),
                color=Colors.DANGER,
                size=18,
            )
        )

    # Left color strip
    strip_color = Colors.SUCCESS if is_done else (Colors.DANGER if overdue else Colors.PRIMARY)

    return ft.Container(
        content=ft.Row(
            controls=[
                # Color indicator strip
                ft.Container(
                    width=4,
                    bgcolor=strip_color,
                    border_radius=Radius.PILL,
                    height=50,
                ),
                # Checkbox
                checkbox,
                # Content Column
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                title_text,
                                *action_controls,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        # Metadata row
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(deadline_icon, size=13, color=deadline_color),
                                        ft.Text(deadline_text, size=Typography.SIZE_CAPTION, color=deadline_color),
                                        *([ft.Text(f"({rem_text})", size=Typography.SIZE_CAPTION, color=deadline_color, weight=ft.FontWeight.W_500)] if rem_text and not is_done else []),
                                    ],
                                    spacing=Spacing.XS,
                                ),
                                ft.Row(controls=badges, spacing=Spacing.XS),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            wrap=True,
                        ),
                    ],
                    spacing=Spacing.XS,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.SM,
        ),
        bgcolor=Colors.SURFACE_RAISED if not is_done else Colors.SURFACE,
        padding=Spacing.CARD_PADDING,
        border_radius=Radius.MD,
        border=ft.Border.all(1, Colors.DANGER if overdue else Colors.BORDER_LIGHT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=Colors.SHADOW,
            offset=ft.Offset(0, 2),
        ),
        on_click=lambda _: on_click(task.id) if on_click else None,
        ink=on_click is not None,
    )
