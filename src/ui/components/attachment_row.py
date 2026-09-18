"""
Attachment row component — displays a file attachment with icon, size, open and delete actions.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.database.models.attachment import Attachment
from src.ui.components.shared import sd_icon_button
from src.utils.i18n import t

ICON_MAP = {
    ".pdf": ft.Icons.PICTURE_AS_PDF,
    ".doc": ft.Icons.DESCRIPTION,
    ".docx": ft.Icons.DESCRIPTION,
    ".xls": ft.Icons.TABLE_CHART,
    ".xlsx": ft.Icons.TABLE_CHART,
    ".csv": ft.Icons.TABLE_CHART,
    ".ppt": ft.Icons.SLIDESHOW,
    ".pptx": ft.Icons.SLIDESHOW,
    ".jpg": ft.Icons.IMAGE,
    ".jpeg": ft.Icons.IMAGE,
    ".png": ft.Icons.IMAGE,
    ".webp": ft.Icons.IMAGE,
    ".zip": ft.Icons.FOLDER_ZIP,
    ".rar": ft.Icons.FOLDER_ZIP,
    ".7z": ft.Icons.FOLDER_ZIP,
    ".txt": ft.Icons.TEXT_SNIPPET,
    ".md": ft.Icons.TEXT_SNIPPET,
    ".py": ft.Icons.CODE,
}


def attachment_row(
    attachment: Attachment,
    on_open: Callable[[int], None],
    on_delete: Callable[[int], None] | None = None,
) -> ft.Container:
    """Row displaying an attachment with icon, name, size, and actions."""
    ext = Path(attachment.file_name).suffix.lower()
    icon_name = ICON_MAP.get(ext, ft.Icons.ATTACH_FILE)

    icon_widget = ft.Icon(
        icon_name,
        color=Colors.PRIMARY,
        size=24,
    )

    details = ft.Column(
        controls=[
            ft.Text(
                attachment.file_name,
                size=Typography.SIZE_BODY,
                weight=ft.FontWeight.W_500,
                color=Colors.TEXT,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                attachment.file_size_display,
                size=Typography.SIZE_CAPTION,
                color=Colors.TEXT_MUTED,
            ),
        ],
        spacing=2,
        expand=True,
    )

    actions: list[ft.Control] = [
        sd_icon_button(
            icon=ft.Icons.OPEN_IN_NEW,
            on_click=lambda _: on_open(attachment.id),
            tooltip=t("tooltip_open_file"),
            color=Colors.PRIMARY,
            size=18,
        )
    ]
    if on_delete:
        actions.append(
            sd_icon_button(
                icon=ft.Icons.DELETE_OUTLINE,
                on_click=lambda _: on_delete(attachment.id),
                tooltip=t("tooltip_delete_attachment"),
                color=Colors.DANGER,
                size=18,
            )
        )

    return ft.Container(
        content=ft.Row(
            controls=[
                icon_widget,
                details,
                ft.Row(controls=actions, spacing=0),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.MD,
        ),
        padding=Spacing.SM,
        bgcolor=Colors.SURFACE_INSET,
        border_radius=Radius.MD,
        border=ft.Border.all(1, Colors.BORDER_LIGHT),
    )
