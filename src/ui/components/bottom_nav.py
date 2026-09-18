"""
Mobile bottom navigation bar component.
"""
from __future__ import annotations
from typing import Callable

import flet as ft

from src.config.settings import Colors, Typography
from src.utils.i18n import t


MOBILE_NAV_ITEMS = [
    ("dashboard", ft.Icons.HOME_OUTLINED, ft.Icons.HOME, "nav_dashboard"),
    ("schedule", ft.Icons.CALENDAR_TODAY_OUTLINED, ft.Icons.CALENDAR_TODAY, "nav_schedule"),
    ("tasks", ft.Icons.ASSIGNMENT_OUTLINED, ft.Icons.ASSIGNMENT, "nav_tasks"),
    ("focus", ft.Icons.TIMER_OUTLINED, ft.Icons.TIMER, "nav_focus"),
    ("settings", ft.Icons.SETTINGS_OUTLINED, ft.Icons.SETTINGS, "nav_settings"),
]


def build_bottom_nav(
    current_route: str,
    on_navigate: Callable[[str], None],
) -> ft.NavigationBar:
    """Build a styled mobile bottom navigation bar."""
    destinations = [
        ft.NavigationBarDestination(
            icon=icon_outline,
            selected_icon=icon_filled,
            label=t(label_key),
        )
        for _, icon_outline, icon_filled, label_key in MOBILE_NAV_ITEMS
    ]

    # Find current index
    routes = [item[0] for item in MOBILE_NAV_ITEMS]
    selected_index = routes.index(current_route) if current_route in routes else 0

    def on_change(e: ft.ControlEvent) -> None:
        idx = int(e.data)
        route = MOBILE_NAV_ITEMS[idx][0]
        on_navigate(route)

    return ft.NavigationBar(
        destinations=destinations,
        selected_index=selected_index,
        on_change=on_change,
        bgcolor=Colors.SURFACE_RAISED,
        indicator_color=Colors.PRIMARY_LIGHTER,
        indicator_shape=ft.RoundedRectangleBorder(radius=12),
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        shadow_color=Colors.SHADOW,
    )
