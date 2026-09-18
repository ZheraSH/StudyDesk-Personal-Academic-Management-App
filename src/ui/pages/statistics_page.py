"""
Statistics page — aggregated academic workload, completion rates, and focus analytics.
"""
from __future__ import annotations
import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography
from src.services.statistics_service import StatisticsService
from src.ui.components.shared import (
    sd_card, sd_section_card, sd_progress_bar, sd_badge, sd_gap,
    safe_update,
)
from src.utils.i18n import t


class StatisticsPage(ft.Column):
    """Academic statistics and productivity metrics page."""

    def __init__(self) -> None:
        self._service = StatisticsService()

        super().__init__(
            controls=[],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=Spacing.LG,
            margin=Spacing.PAGE_PADDING,
        )
        self.refresh()

    def refresh(self) -> None:
        task_stats = self._service.get_task_stats()
        weekly_stats = self._service.get_weekly_stats()

        # Stat cards row
        stat_cards = ft.Row(
            controls=[
                self._metric_box(t("active_tasks"), str(task_stats.active), ft.Icons.CHECK_BOX_OUTLINE_BLANK, Colors.PRIMARY),
                self._metric_box(t("completed_tasks"), str(task_stats.completed), ft.Icons.CHECK_CIRCLE, Colors.SUCCESS),
                self._metric_box(t("this_week"), str(task_stats.completed_this_week), ft.Icons.DATE_RANGE, Colors.INFO),
                self._metric_box(t("urgency_overdue"), str(task_stats.overdue), ft.Icons.WARNING_AMBER, Colors.DANGER if task_stats.overdue > 0 else Colors.TEXT_MUTED),
            ],
            spacing=Spacing.MD,
        )

        # Workload & Focus section
        workload_hours = task_stats.total_estimated_minutes // 60
        workload_mins = task_stats.total_estimated_minutes % 60
        workload_str = t("duration_hours_min", h=workload_hours, m=workload_mins) if workload_hours > 0 else t("duration_min", m=workload_mins)

        focus_h = weekly_stats.focus_minutes // 60
        focus_m = weekly_stats.focus_minutes % 60
        focus_str = f"{focus_h}h {focus_m}m"

        total_tasks_this_week = weekly_stats.tasks_completed + weekly_stats.tasks_active
        comp_rate = (weekly_stats.tasks_completed / total_tasks_this_week) if total_tasks_this_week > 0 else 0.0

        productivity_card = sd_section_card(
            title=t("weekly_productivity"),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(t("workload_remaining"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                                    ft.Text(workload_str, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.BOLD, color=Colors.PRIMARY_DARK),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(t("focus_time_logged"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                                    ft.Text(focus_str, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.BOLD, color=Colors.PRIMARY),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=Spacing.LG,
                    ),
                    sd_gap(Spacing.MD),
                    sd_progress_bar(
                        value=comp_rate,
                        label=t("completion_rate_label", pct=int(comp_rate * 100), done=weekly_stats.tasks_completed, total=total_tasks_this_week),
                        color=Colors.SUCCESS if comp_rate >= 0.75 else Colors.PRIMARY,
                    ),
                ],
                spacing=Spacing.SM,
            ),
        )

        # Academic health notice
        if task_stats.overdue > 0:
            health_notice = sd_card(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.NOTIFICATION_IMPORTANT, color=Colors.DANGER, size=24),
                        ft.Column(
                            controls=[
                                ft.Text(t("overdue_alert_title", count=task_stats.overdue), size=Typography.SIZE_BODY_LARGE, weight=ft.FontWeight.W_600, color=Colors.DANGER),
                                ft.Text(t("overdue_alert_sub"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=Spacing.MD,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=Colors.DANGER_BG,
                border_color=Colors.DANGER,
            )
        else:
            health_notice = sd_card(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED, color=Colors.SUCCESS, size=24),
                        ft.Column(
                            controls=[
                                ft.Text(t("on_track_title"), size=Typography.SIZE_BODY_LARGE, weight=ft.FontWeight.W_600, color=Colors.SUCCESS),
                                ft.Text(t("on_track_sub"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=Spacing.MD,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=Colors.SUCCESS_BG,
                border_color=Colors.SUCCESS,
            )

        self.controls = [
            ft.Text(t("stats_title"), size=Typography.SIZE_PAGE_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
            stat_cards,
            health_notice,
            productivity_card,
        ]
        safe_update(self)

    def _metric_box(self, label: str, value: str, icon: str, color: str) -> ft.Container:
        return sd_card(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=24),
                        bgcolor=Colors.SURFACE_INSET,
                        padding=Spacing.SM,
                        border_radius=Radius.MD,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(label, size=Typography.SIZE_CAPTION, color=Colors.TEXT_MUTED),
                            ft.Text(value, size=Typography.SIZE_SECTION_TITLE, weight=ft.FontWeight.BOLD, color=Colors.TEXT),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=Spacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
        )
