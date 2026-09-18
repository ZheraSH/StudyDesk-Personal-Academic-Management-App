"""
Schedule card component — displays individual schedule block with course, time, room, and type.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.schedule import Schedule, ScheduleType
from src.ui.components.shared import sd_badge, sd_icon_button
from src.utils.i18n import t

TYPE_COLOR_MAP = {
    ScheduleType.LECTURE: Colors.SCHEDULE_LECTURE,
    ScheduleType.PRACTICUM: Colors.SCHEDULE_PRACTICUM,
    ScheduleType.OTHER: Colors.SCHEDULE_OTHER,
    "Lecture": Colors.SCHEDULE_LECTURE,
    "Practicum": Colors.SCHEDULE_PRACTICUM,
    "Other": Colors.SCHEDULE_OTHER,
}


def schedule_card(
    schedule: Schedule,
    on_click: Callable[[], None] | None = None,
    on_edit: Callable[[], None] | None = None,
    on_delete: Callable[[], None] | None = None,
    compact: bool = False,
) -> ft.Container:
    """Styled schedule card with skeuomorphic border strip and course metadata."""
    raw_type = schedule.schedule_type.value if hasattr(schedule.schedule_type, "value") else str(schedule.schedule_type)
    accent_color = TYPE_COLOR_MAP.get(raw_type, Colors.PRIMARY)

    course_name = schedule.course.name if schedule.course else t("unknown_course")
    course_code = schedule.course.code if schedule.course and schedule.course.code else ""
    room_text = t("room_label", room=schedule.room) if schedule.room else t("no_room")
    time_str = f"{schedule.start_time.strftime('%H:%M')} – {schedule.end_time.strftime('%H:%M')}"

    badge = sd_badge(
        text=raw_type,
        bgcolor=accent_color,
        color=Colors.TEXT_ON_PRIMARY,
        small=True,
    )

    action_controls: list[ft.Control] = []
    if on_edit:
        action_controls.append(
            sd_icon_button(
                icon=ft.Icons.EDIT_OUTLINED,
                on_click=lambda _: on_edit(),
                tooltip=t("tooltip_edit_schedule"),
                size=18,
            )
        )
    if on_delete:
        action_controls.append(
            sd_icon_button(
                icon=ft.Icons.DELETE_OUTLINE,
                on_click=lambda _: on_delete(),
                tooltip=t("tooltip_delete_schedule"),
                color=Colors.DANGER,
                size=18,
            )
        )

    if compact:
        content = ft.Row(
            controls=[
                ft.Container(
                    width=4,
                    bgcolor=accent_color,
                    border_radius=Radius.PILL,
                    height=36,
                ),
                ft.Column(
                    controls=[
                        ft.Text(course_name, size=Typography.SIZE_BODY, weight=ft.FontWeight.W_600, color=Colors.TEXT),
                        ft.Text(f"{time_str} • {room_text}", size=Typography.SIZE_CAPTION, color=Colors.TEXT_MUTED),
                    ],
                    spacing=2,
                    expand=True,
                ),
                badge,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    else:
        content = ft.Row(
            controls=[
                ft.Container(
                    width=6,
                    bgcolor=accent_color,
                    border_radius=Radius.PILL,
                    height=56,
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"{course_code} - {course_name}" if course_code else course_name,
                                    size=Typography.SIZE_CARD_TITLE,
                                    weight=ft.FontWeight.W_600,
                                    color=Colors.TEXT,
                                    expand=True,
                                ),
                                badge,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.ACCESS_TIME, size=14, color=Colors.PRIMARY),
                                        ft.Text(time_str, size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                                    ],
                                    spacing=Spacing.XS,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.ROOM_OUTLINED, size=14, color=Colors.PRIMARY),
                                        ft.Text(room_text, size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                                    ],
                                    spacing=Spacing.XS,
                                ),
                            ],
                            spacing=Spacing.LG,
                        ),
                        *([ft.Text(schedule.notes, size=Typography.SIZE_CAPTION, italic=True, color=Colors.TEXT_MUTED)] if schedule.notes else []),
                    ],
                    spacing=Spacing.XS,
                    expand=True,
                ),
                *([ft.Row(controls=action_controls, spacing=0)] if action_controls else []),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.MD,
        )

    return ft.Container(
        content=content,
        bgcolor=Colors.SURFACE_RAISED,
        padding=Spacing.CARD_PADDING if not compact else Spacing.MD,
        border_radius=Radius.MD,
        border=ft.Border.all(1, Colors.BORDER_LIGHT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=Colors.SHADOW,
            offset=ft.Offset(0, 2),
        ),
        on_click=lambda _: on_click() if on_click else None,
        ink=on_click is not None,
    )
