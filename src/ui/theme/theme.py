"""
StudyDesk Flet theme configuration.
Muted Royal Purple Skeuomorphism design system.
"""
from __future__ import annotations

import flet as ft

from src.config.settings import Colors, Typography


def get_theme() -> ft.Theme:
    """Return the StudyDesk light theme."""
    return ft.Theme(
        color_scheme_seed=Colors.PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=Colors.PRIMARY,
            primary_container=Colors.PRIMARY_LIGHT,
            on_primary=Colors.TEXT_ON_PRIMARY,
            secondary=Colors.PRIMARY_LIGHT,
            secondary_container=Colors.SURFACE,
            on_secondary=Colors.TEXT,
            surface=Colors.SURFACE,
            on_surface=Colors.TEXT,
            surface_container=Colors.SURFACE_RAISED,
            outline=Colors.BORDER,
            error=Colors.DANGER,
            on_error=Colors.TEXT_ON_PRIMARY,
        ),
        scaffold_bgcolor=Colors.BACKGROUND,
        card_bgcolor=Colors.SURFACE,
        font_family=Typography.FONT_FAMILY,
        visual_density=ft.VisualDensity.STANDARD,
        use_material3=True,
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(
                size=Typography.SIZE_PAGE_TITLE,
                weight=ft.FontWeight.W_600,
                color=Colors.TEXT,
            ),
            title_large=ft.TextStyle(
                size=Typography.SIZE_SECTION_TITLE,
                weight=ft.FontWeight.W_600,
                color=Colors.TEXT,
            ),
            title_medium=ft.TextStyle(
                size=Typography.SIZE_CARD_TITLE,
                weight=ft.FontWeight.W_600,
                color=Colors.TEXT,
            ),
            body_large=ft.TextStyle(
                size=Typography.SIZE_BODY_LARGE,
                color=Colors.TEXT,
            ),
            body_medium=ft.TextStyle(
                size=Typography.SIZE_BODY,
                color=Colors.TEXT,
            ),
            body_small=ft.TextStyle(
                size=Typography.SIZE_SMALL,
                color=Colors.TEXT_MUTED,
            ),
            label_small=ft.TextStyle(
                size=Typography.SIZE_CAPTION,
                color=Colors.TEXT_MUTED,
            ),
        ),
    )
