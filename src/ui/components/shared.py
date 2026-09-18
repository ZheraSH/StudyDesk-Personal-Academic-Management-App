"""
Shared Flet UI component helpers.
All styled widgets for StudyDesk live here or in individual component files.
"""
from __future__ import annotations
from typing import Callable, Any

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.utils.i18n import t


# ─────────────────────────── Cards ───────────────────────────────────

def sd_card(
    content: ft.Control,
    padding: int | ft.Padding = Spacing.CARD_PADDING,
    margin: ft.Margin | int | None = None,
    bgcolor: str = Colors.SURFACE_RAISED,
    border_color: str = Colors.BORDER_LIGHT,
    shadow: bool = True,
    on_click: Callable | None = None,
    expand: bool | int | None = None,
    **kwargs: Any,
) -> ft.Container:
    """Standard StudyDesk card — physical paper panel aesthetic."""
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        padding=padding,
        margin=margin,
        border_radius=Radius.LG,
        border=ft.Border.all(1, border_color),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=6,
            color=Colors.SHADOW,
            offset=ft.Offset(0, 2),
        ) if shadow else None,
        on_click=on_click,
        ink=on_click is not None,
        expand=expand,
        **kwargs,
    )


def sd_section_card(
    title: str,
    content: ft.Control,
    title_action: ft.Control | None = None,
    **kwargs: Any,
) -> ft.Container:
    """A titled section card."""
    header_row = ft.Row(
        controls=[
            ft.Text(
                title,
                size=Typography.SIZE_SMALL,
                weight=ft.FontWeight.W_600,
                color=Colors.PRIMARY,
                style=ft.TextStyle(letter_spacing=1.2),
            ),
            *([ title_action] if title_action else []),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )
    return sd_card(
        content=ft.Column(
            controls=[header_row, ft.Divider(height=1, color=Colors.BORDER_LIGHT), content],
            spacing=Spacing.MD,
            tight=True,
        ),
        **kwargs,
    )


# ─────────────────────────── Buttons ─────────────────────────────────

def sd_primary_button(
    text: str,
    on_click: Callable,
    icon: str | None = None,
    disabled: bool = False,
    width: int | None = None,
) -> ft.FilledButton:
    """Raised primary purple button."""
    return ft.FilledButton(
        content=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        width=width,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: Colors.PRIMARY,
                ft.ControlState.HOVERED: Colors.PRIMARY_DARK,
                ft.ControlState.PRESSED: Colors.PRIMARY_DARK,
                ft.ControlState.DISABLED: Colors.TEXT_DISABLED,
            },
            color={
                ft.ControlState.DEFAULT: Colors.TEXT_ON_PRIMARY,
                ft.ControlState.DISABLED: Colors.SURFACE,
            },
            elevation={
                ft.ControlState.DEFAULT: 2,
                ft.ControlState.HOVERED: 4,
                ft.ControlState.PRESSED: 1,
            },
            shape=ft.RoundedRectangleBorder(radius=Radius.MD),
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
        ),
    )


def sd_secondary_button(
    text: str,
    on_click: Callable,
    icon: str | None = None,
    disabled: bool = False,
) -> ft.OutlinedButton:
    """Outlined secondary button with purple accent."""
    return ft.OutlinedButton(
        content=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: Colors.PRIMARY,
                ft.ControlState.HOVERED: Colors.PRIMARY_DARK,
                ft.ControlState.DISABLED: Colors.TEXT_DISABLED,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(1, Colors.BORDER_FOCUS),
                ft.ControlState.HOVERED: ft.BorderSide(1.5, Colors.PRIMARY),
                ft.ControlState.DISABLED: ft.BorderSide(1, Colors.BORDER),
            },
            shape=ft.RoundedRectangleBorder(radius=Radius.MD),
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
        ),
    )


def sd_danger_button(
    text: str,
    on_click: Callable,
    icon: str | None = None,
) -> ft.TextButton:
    """Danger action button in muted red."""
    return ft.TextButton(
        content=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: Colors.DANGER,
                ft.ControlState.HOVERED: Colors.PRIMARY_DARK,
            },
        ),
    )


def sd_icon_button(
    icon: str,
    on_click: Callable,
    tooltip: str | None = None,
    color: str = Colors.TEXT_MUTED,
    size: int = 20,
) -> ft.IconButton:
    """Simple icon button."""
    return ft.IconButton(
        icon=icon,
        on_click=on_click,
        tooltip=tooltip,
        icon_color=color,
        icon_size=size,
    )


# ─────────────────────────── Labels / Badges ─────────────────────────

def sd_badge(
    text: str,
    bgcolor: str = Colors.PRIMARY,
    color: str = Colors.TEXT_ON_PRIMARY,
    small: bool = False,
) -> ft.Container:
    """Pill-shaped badge label."""
    return ft.Container(
        content=ft.Text(
            text,
            size=Typography.SIZE_CAPTION if small else Typography.SIZE_SMALL,
            weight=ft.FontWeight.W_600,
            color=color,
        ),
        bgcolor=bgcolor,
        padding=ft.Padding.symmetric(
            horizontal=Spacing.SM if small else Spacing.MD,
            vertical=2 if small else 4,
        ),
        border_radius=Radius.PILL,
    )


def sd_status_badge(status: str) -> ft.Container:
    """Task status badge with appropriate color."""
    COLOR_MAP = {
        "Inbox": (Colors.STATUS_INBOX, Colors.TEXT_ON_PRIMARY),
        "Planned": (Colors.STATUS_PLANNED, Colors.TEXT_ON_PRIMARY),
        "In Progress": (Colors.STATUS_IN_PROGRESS, Colors.TEXT_ON_PRIMARY),
        "Completed": (Colors.STATUS_COMPLETED, Colors.TEXT_ON_PRIMARY),
        "Archived": (Colors.STATUS_ARCHIVED, Colors.TEXT_ON_PRIMARY),
    }
    bgcolor, color = COLOR_MAP.get(status, (Colors.SURFACE, Colors.TEXT))
    key = f"status_{status.lower().replace(' ', '_')}"
    label = t(key)
    return sd_badge(label, bgcolor=bgcolor, color=color)


def sd_priority_badge(priority: str, small: bool = False) -> ft.Container:
    """Priority badge with appropriate color."""
    COLOR_MAP = {
        "Low": (Colors.PRIORITY_LOW, Colors.TEXT_ON_PRIMARY),
        "Medium": (Colors.PRIORITY_MEDIUM, Colors.TEXT_ON_PRIMARY),
        "High": (Colors.PRIORITY_HIGH, Colors.TEXT_ON_PRIMARY),
        "Urgent": (Colors.PRIORITY_URGENT, Colors.TEXT_ON_PRIMARY),
    }
    bgcolor, color = COLOR_MAP.get(priority, (Colors.SURFACE, Colors.TEXT))
    key = f"priority_{priority.lower()}"
    label = t(key)
    return sd_badge(label, bgcolor=bgcolor, color=color, small=small)


def sd_urgency_badge(urgency: str) -> ft.Container:
    """Deadline urgency badge."""
    COLOR_MAP = {
        "overdue": (Colors.STATUS_OVERDUE, Colors.TEXT_ON_PRIMARY),
        "critical": (Colors.DANGER, Colors.TEXT_ON_PRIMARY),
        "high": (Colors.WARNING, Colors.TEXT_ON_PRIMARY),
        "moderate": (Colors.PRIMARY_LIGHT, Colors.TEXT_ON_PRIMARY),
        "normal": (Colors.SURFACE, Colors.TEXT_MUTED),
        "none": (Colors.SURFACE, Colors.TEXT_MUTED),
    }
    bgcolor, color = COLOR_MAP.get(urgency, (Colors.SURFACE, Colors.TEXT_MUTED))
    key = f"urgency_{urgency}"
    label = t(key).upper() if urgency != "none" else "—"
    return sd_badge(label, bgcolor=bgcolor, color=color, small=True)


# ─────────────────────────── Text Helpers ────────────────────────────

def sd_title(text: str, size: int = Typography.SIZE_PAGE_TITLE) -> ft.Text:
    return ft.Text(text, size=size, weight=ft.FontWeight.W_600, color=Colors.TEXT)


def sd_section_title(text: str) -> ft.Text:
    return ft.Text(
        text,
        size=Typography.SIZE_SMALL,
        weight=ft.FontWeight.W_600,
        color=Colors.PRIMARY,
        style=ft.TextStyle(letter_spacing=1.2),
    )


def sd_body(text: str, color: str = Colors.TEXT, size: int = Typography.SIZE_BODY) -> ft.Text:
    return ft.Text(text, size=size, color=color)


def sd_muted(text: str, size: int = Typography.SIZE_SMALL) -> ft.Text:
    return ft.Text(text, size=size, color=Colors.TEXT_MUTED)


def sd_caption(text: str) -> ft.Text:
    return ft.Text(text, size=Typography.SIZE_CAPTION, color=Colors.TEXT_MUTED)


# ─────────────────────────── Dividers / Gaps ─────────────────────────

def sd_divider() -> ft.Divider:
    return ft.Divider(height=1, color=Colors.BORDER_LIGHT)


def sd_gap(height: int = Spacing.MD) -> ft.Container:
    return ft.Container(height=height)


def sd_hgap(width: int = Spacing.MD) -> ft.Container:
    return ft.Container(width=width)


# ─────────────────────────── Empty State ─────────────────────────────

def sd_empty_state(
    icon: str,
    title: str,
    subtitle: str = "",
    action: ft.Control | None = None,
) -> ft.Container:
    """Friendly empty state widget."""
    controls: list[ft.Control] = [
        ft.Icon(icon, size=48, color=Colors.BORDER),
        sd_gap(Spacing.MD),
        ft.Text(title, size=Typography.SIZE_CARD_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=Typography.SIZE_BODY, color=Colors.TEXT_DISABLED, text_align=ft.TextAlign.CENTER))
    if action:
        controls += [sd_gap(Spacing.LG), action]

    return ft.Container(
        content=ft.Column(controls=controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=Spacing.SM),
        alignment=ft.Alignment.CENTER,
        padding=Spacing.XXXL,
    )


# ─────────────────────────── Inputs ──────────────────────────────────

def sd_text_field(
    label: str,
    value: str = "",
    hint: str = "",
    on_change: Callable | None = None,
    password: bool = False,
    multiline: bool = False,
    max_lines: int = 1,
    prefix_icon: str | None = None,
    suffix: ft.Control | None = None,
    autofocus: bool = False,
    read_only: bool = False,
    expand: bool = False,
) -> ft.TextField:
    border = {
        ft.ControlState.DEFAULT: ft.OutlineInputBorder(
            border_radius=ft.BorderRadius.all(Radius.MD),
            side=ft.BorderSide(1, Colors.BORDER),
        ),
        ft.ControlState.FOCUSED: ft.OutlineInputBorder(
            border_radius=ft.BorderRadius.all(Radius.MD),
            side=ft.BorderSide(1.5, Colors.PRIMARY),
        ),
    }
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint,
        on_change=on_change,
        password=password,
        multiline=multiline,
        min_lines=1,
        max_lines=max_lines,
        prefix_icon=prefix_icon,
        suffix=suffix,
        autofocus=autofocus,
        read_only=read_only,
        expand=expand,
        border=border,
        bgcolor=Colors.SURFACE_INSET,
        label_style=ft.TextStyle(color=Colors.TEXT_MUTED, size=Typography.SIZE_SMALL),
        content_padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.MD),
    )


def sd_dropdown(
    label: str,
    options: list[ft.dropdown.Option] | list[ft.DropdownOption],
    value: str | None = None,
    on_change: Callable | None = None,
    expand: bool = False,
) -> ft.Dropdown:
    """Styled dropdown."""
    border = {
        ft.ControlState.DEFAULT: ft.OutlineInputBorder(
            border_radius=ft.BorderRadius.all(Radius.MD),
            side=ft.BorderSide(1, Colors.BORDER),
        ),
        ft.ControlState.FOCUSED: ft.OutlineInputBorder(
            border_radius=ft.BorderRadius.all(Radius.MD),
            side=ft.BorderSide(1.5, Colors.PRIMARY),
        ),
    }
    return ft.Dropdown(
        label=label,
        options=options,
        value=value,
        on_select=on_change,
        expand=expand,
        border=border,
        bgcolor=Colors.SURFACE_INSET,
        label_style=ft.TextStyle(color=Colors.TEXT_MUTED, size=Typography.SIZE_SMALL),
    )


# ─────────────────────────── Progress Bar ────────────────────────────

def sd_progress_bar(
    value: float,  # 0.0 to 1.0
    label: str = "",
    color: str = Colors.PRIMARY,
) -> ft.Column:
    """Progress bar with optional label."""
    controls: list[ft.Control] = []
    if label:
        controls.append(sd_caption(label))
    controls.append(
        ft.ProgressBar(
            value=value,
            color=color,
            bgcolor=Colors.BORDER_LIGHT,
            border_radius=Radius.PILL,
            height=6,
        )
    )
    return ft.Column(controls=controls, spacing=4, tight=True)


# ─────────────────────────── Loading ─────────────────────────────────

def sd_loading() -> ft.Container:
    """Centered loading indicator."""
    return ft.Container(
        content=ft.ProgressRing(color=Colors.PRIMARY, stroke_width=3),
        alignment=ft.Alignment.CENTER,
        padding=Spacing.XXXL,
    )


# ─────────────────────────── Error Banner ────────────────────────────

def sd_error_banner(message: str) -> ft.Container:
    """Friendly inline error message."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=Colors.DANGER, size=16),
                ft.Text(message, color=Colors.DANGER, size=Typography.SIZE_SMALL, expand=True),
            ],
            spacing=Spacing.SM,
        ),
        bgcolor=Colors.DANGER_BG,
        padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
        border_radius=Radius.SM,
        border=ft.Border.all(1, Colors.DANGER),
    )


def sd_success_banner(message: str) -> ft.Container:
    """Friendly inline success message."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=Colors.SUCCESS, size=16),
                ft.Text(message, color=Colors.SUCCESS, size=Typography.SIZE_SMALL, expand=True),
            ],
            spacing=Spacing.SM,
        ),
        bgcolor=Colors.SUCCESS_BG,
        padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
        border_radius=Radius.SM,
        border=ft.Border.all(1, Colors.SUCCESS),
    )


def safe_update(control: ft.Control) -> None:
    """Safely update a control if it is attached to a page."""
    try:
        control.update()
    except RuntimeError:
        pass
