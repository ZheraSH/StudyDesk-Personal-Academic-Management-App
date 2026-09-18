"""
Focus page — Pomodoro study timer with preset selectors, task linking, and session stats.
"""
from __future__ import annotations
import threading
import time
from typing import Callable

import flet as ft

from src.config.settings import Colors, Spacing, Radius, Typography, FOCUS_PRESETS
from src.services.focus_service import FocusService
from src.services.task_service import TaskService
from src.ui.components.shared import (
    sd_card, sd_section_card, sd_badge, sd_primary_button, sd_secondary_button,
    sd_dropdown, sd_gap, sd_hgap, safe_update,
)
from src.utils.i18n import t


class FocusPage(ft.Column):
    """Pomodoro focus timer with presets, session recording, and progress tracking."""

    def __init__(self, initial_task_id: int | None = None) -> None:
        self._initial_task_id = initial_task_id
        self._focus_service = FocusService()
        self._task_service = TaskService()

        # State
        self._preset = "25/5"
        self._focus_duration = 25 * 60  # seconds
        self._break_duration = 5 * 60
        self._remaining_seconds = self._focus_duration
        self._is_running = False
        self._is_break = False
        self._current_session_id: int | None = None
        self._timer_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # UI elements
        self._timer_display = ft.Text(
            self._format_time(self._remaining_seconds),
            size=64,
            weight=ft.FontWeight.BOLD,
            color=Colors.PRIMARY,
        )

        self._mode_badge = sd_badge(t("focus_session_badge"), bgcolor=Colors.PRIMARY)

        # Task dropdown
        tasks = self._task_service.get_all_active()
        task_options = [ft.dropdown.Option(key="none", text=t("no_specific_task"))] + [
            ft.dropdown.Option(key=str(t.id), text=t.title)
            for t in tasks
        ]
        selected_task_key = str(initial_task_id) if initial_task_id else "none"
        self._task_dropdown = sd_dropdown(
            label=t("linked_task_label"),
            options=task_options,
            value=selected_task_key,
            expand=True,
        )

        self._start_pause_btn = sd_primary_button(
            t("btn_start_focus"),
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._toggle_timer,
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
        today_mins = self._focus_service.get_today_minutes()
        week_mins = self._focus_service.get_week_minutes()
        recent_sessions = self._focus_service.get_recent(5)

        # Preset buttons
        preset_buttons: list[ft.Control] = []
        for p_name in ("15/5", "25/5", "50/10"):
            is_active = p_name == self._preset
            preset_buttons.append(
                ft.FilledButton(
                    p_name,
                    on_click=lambda _, p=p_name: self._set_preset(p),
                    style=ft.ButtonStyle(
                        bgcolor=Colors.PRIMARY if is_active else Colors.SURFACE_INSET,
                        color=Colors.TEXT_ON_PRIMARY if is_active else Colors.TEXT,
                        shape=ft.RoundedRectangleBorder(radius=Radius.MD),
                    ),
                )
            )

        # Timer Card
        timer_card = sd_card(
            content=ft.Column(
                controls=[
                    self._mode_badge,
                    sd_gap(Spacing.MD),
                    self._timer_display,
                    sd_gap(Spacing.MD),
                    ft.Row(
                        controls=preset_buttons,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=Spacing.MD,
                    ),
                    sd_gap(Spacing.LG),
                    ft.Row(
                        controls=[
                            self._start_pause_btn,
                            sd_secondary_button(t("btn_reset"), icon=ft.Icons.REFRESH, on_click=self._reset_timer),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=Spacing.MD,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.XS,
            ),
            padding=Spacing.XXXL,
        )

        # Stats Card
        stats_card = ft.Row(
            controls=[
                sd_card(
                    content=ft.Column(
                        controls=[
                            ft.Text(t("today_focus"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                            ft.Text(t("focus_minutes_label", minutes=today_mins), size=Typography.SIZE_PAGE_TITLE, weight=ft.FontWeight.BOLD, color=Colors.PRIMARY),
                        ],
                        spacing=2,
                    ),
                    expand=True,
                ),
                sd_card(
                    content=ft.Column(
                        controls=[
                            ft.Text(t("this_week"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED),
                            ft.Text(t("focus_hours_minutes", hours=week_mins // 60, minutes=week_mins % 60), size=Typography.SIZE_PAGE_TITLE, weight=ft.FontWeight.BOLD, color=Colors.PRIMARY_DARK),
                        ],
                        spacing=2,
                    ),
                    expand=True,
                ),
            ],
            spacing=Spacing.MD,
        )

        # Recent sessions
        history_rows: list[ft.Control] = []
        for s in recent_sessions:
            task_title = s.task.title if s.task else t("general_study")
            dur = t("focus_minutes_label", minutes=s.duration_minutes) if s.duration_minutes else t("less_than_1_min")
            date_str = s.started_at.strftime("%d %b, %H:%M")
            history_rows.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE if s.completed else ft.Icons.CANCEL, size=16, color=Colors.SUCCESS if s.completed else Colors.TEXT_MUTED),
                            ft.Text(task_title, size=Typography.SIZE_BODY, color=Colors.TEXT, expand=True),
                            ft.Text(dur, size=Typography.SIZE_SMALL, weight=ft.FontWeight.W_600, color=Colors.PRIMARY),
                            ft.Text(date_str, size=Typography.SIZE_CAPTION, color=Colors.TEXT_MUTED),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=Spacing.MD,
                    ),
                    padding=Spacing.SM,
                    bgcolor=Colors.SURFACE_INSET,
                    border_radius=Radius.SM,
                )
            )

        if not recent_sessions:
            history_rows.append(
                ft.Text(t("no_recent_sessions"), size=Typography.SIZE_SMALL, color=Colors.TEXT_MUTED)
            )

        history_card = sd_section_card(
            title=t("recent_sessions_title"),
            content=ft.Column(controls=history_rows, spacing=Spacing.SM),
        )

        self.controls = [
            ft.Text(t("focus_title"), size=Typography.SIZE_PAGE_TITLE, weight=ft.FontWeight.W_600, color=Colors.TEXT),
            self._task_dropdown,
            timer_card,
            stats_card,
            history_card,
        ]
        safe_update(self)

    def _set_preset(self, preset_name: str) -> None:
        if self._is_running:
            return
        self._preset = preset_name
        focus_m, break_m = FOCUS_PRESETS.get(preset_name, (25, 5))
        self._focus_duration = focus_m * 60
        self._break_duration = break_m * 60
        self._remaining_seconds = self._focus_duration
        self._is_break = False
        self._timer_display.value = self._format_time(self._remaining_seconds)
        self.refresh()

    def _format_time(self, total_seconds: int) -> str:
        m = total_seconds // 60
        s = total_seconds % 60
        return f"{m:02d}:{s:02d}"

    def _toggle_timer(self, _: ft.ControlEvent) -> None:
        if self._is_running:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self) -> None:
        self._is_running = True
        self._start_pause_btn.text = t("btn_pause")
        self._start_pause_btn.icon = ft.Icons.PAUSE
        self._stop_event.clear()

        # If starting fresh focus session, record in DB
        if not self._is_break and self._current_session_id is None:
            task_id = (
                int(self._task_dropdown.value)
                if self._task_dropdown.value and self._task_dropdown.value != "none"
                else None
            )
            fs, _ = self._focus_service.start_session(task_id)
            if fs:
                self._current_session_id = fs.id

        self._timer_thread = threading.Thread(target=self._run_countdown, daemon=True)
        self._timer_thread.start()
        self.update()

    def _pause_timer(self) -> None:
        self._is_running = False
        self._stop_event.set()
        self._start_pause_btn.text = t("btn_resume")
        self._start_pause_btn.icon = ft.Icons.PLAY_ARROW
        self.update()

    def _reset_timer(self, _: ft.ControlEvent) -> None:
        self._stop_event.set()
        self._is_running = False
        self._is_break = False
        if self._current_session_id:
            self._focus_service.end_session(self._current_session_id, completed=False)
            self._current_session_id = None

        focus_m, _ = FOCUS_PRESETS.get(self._preset, (25, 5))
        self._remaining_seconds = focus_m * 60
        self._timer_display.value = self._format_time(self._remaining_seconds)
        self._mode_badge.content.value = t("focus_session_badge")
        self._mode_badge.bgcolor = Colors.PRIMARY
        self._start_pause_btn.text = t("btn_start_focus")
        self._start_pause_btn.icon = ft.Icons.PLAY_ARROW
        self.refresh()

    def _run_countdown(self) -> None:
        while self._is_running and self._remaining_seconds > 0:
            if self._stop_event.wait(1.0):
                break
            self._remaining_seconds -= 1
            self._timer_display.value = self._format_time(self._remaining_seconds)
            try:
                self._timer_display.update()
            except Exception:
                break

        if self._remaining_seconds <= 0 and self._is_running:
            self._on_interval_completed()

    def _on_interval_completed(self) -> None:
        self._is_running = False
        if not self._is_break:
            # Focus ended -> complete session and switch to break
            if self._current_session_id:
                self._focus_service.end_session(self._current_session_id, completed=True)
                self._current_session_id = None
            self._is_break = True
            self._remaining_seconds = self._break_duration
            self._mode_badge.content.value = t("break_session_badge")
            self._mode_badge.bgcolor = Colors.SUCCESS
            self._timer_display.value = self._format_time(self._remaining_seconds)
            self._start_pause_btn.text = t("btn_start_break")
            self._start_pause_btn.icon = ft.Icons.PLAY_ARROW
        else:
            # Break ended -> switch back to focus
            self._is_break = False
            self._remaining_seconds = self._focus_duration
            self._mode_badge.content.value = t("focus_session_badge")
            self._mode_badge.bgcolor = Colors.PRIMARY
            self._timer_display.value = self._format_time(self._remaining_seconds)
            self._start_pause_btn.text = t("btn_start_focus")
            self._start_pause_btn.icon = ft.Icons.PLAY_ARROW

        try:
            self.refresh()
        except Exception:
            pass
