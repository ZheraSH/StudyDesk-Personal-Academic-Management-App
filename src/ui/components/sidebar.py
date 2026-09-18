"""
Desktop sidebar navigation component.
Raised physical button feel with active state indicators.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.utils.i18n import t
from src.ui.components.shared import safe_update


NAV_ITEMS = [
    ("dashboard", ft.Icons.DASHBOARD_OUTLINED, ft.Icons.DASHBOARD, "nav_dashboard"),
    ("schedule", ft.Icons.CALENDAR_TODAY_OUTLINED, ft.Icons.CALENDAR_TODAY, "nav_schedule"),
    ("tasks", ft.Icons.ASSIGNMENT_OUTLINED, ft.Icons.ASSIGNMENT, "nav_tasks"),
    ("focus", ft.Icons.TIMER_OUTLINED, ft.Icons.TIMER, "nav_focus"),
    ("statistics", ft.Icons.BAR_CHART_OUTLINED, ft.Icons.BAR_CHART, "nav_statistics"),
    ("settings", ft.Icons.SETTINGS_OUTLINED, ft.Icons.SETTINGS, "nav_settings"),
]


class Sidebar(ft.Column):
    """Desktop sidebar with StudyDesk navigation."""

    def __init__(
        self,
        current_route: str,
        on_navigate: Callable[[str], None],
    ) -> None:
        self._current_route = current_route
        self._on_navigate = on_navigate

        super().__init__(
            controls=self._build_controls(),
            width=220,
            spacing=0,
        )

    def _build_controls(self) -> list[ft.Control]:
        controls: list[ft.Control] = [
            self._build_logo(),
            ft.Container(height=Spacing.LG),
            ft.Divider(height=1, color=Colors.BORDER_LIGHT),
            ft.Container(height=Spacing.MD),
        ]

        for route, icon_outline, icon_filled, label in NAV_ITEMS:
            controls.append(self._build_nav_item(route, icon_outline, icon_filled, label))

        controls.append(ft.Container(expand=True))  # Spacer
        return controls

    def _build_logo(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.BOOK, color=Colors.TEXT_ON_PRIMARY, size=18),
                        bgcolor=Colors.PRIMARY,
                        padding=Spacing.SM,
                        border_radius=Radius.MD,
                    ),
                    ft.Text(
                        "StudyDesk",
                        size=Typography.SIZE_CARD_TITLE,
                        weight=ft.FontWeight.W_600,
                        color=Colors.TEXT,
                    ),
                ],
                spacing=Spacing.SM,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.all(Spacing.LG),
        )

    def _build_nav_item(
        self, route: str, icon_outline: str, icon_filled: str, label: str
    ) -> ft.Control:
        is_active = self._current_route == route
        bg = Colors.PRIMARY if is_active else "transparent"
        icon = icon_filled if is_active else icon_outline
        text_color = Colors.TEXT_ON_PRIMARY if is_active else Colors.TEXT_MUTED
        icon_color = Colors.TEXT_ON_PRIMARY if is_active else Colors.TEXT_MUTED

        def on_click(e: ft.ControlEvent, r: str = route) -> None:
            self._on_navigate(r)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=icon_color, size=18),
                    ft.Text(
                        t(label),
                        size=Typography.SIZE_BODY,
                        color=text_color,
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=Spacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=bg,
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            border_radius=ft.BorderRadius.only(
                top_right=Radius.MD, bottom_right=Radius.MD
            ) if is_active else Radius.MD,
            margin=ft.Margin.only(right=Spacing.MD, bottom=2),
            on_click=on_click,
            ink=True,
        )

    def update_route(self, new_route: str) -> None:
        self._current_route = new_route
        self.controls = self._build_controls()
        safe_update(self)
