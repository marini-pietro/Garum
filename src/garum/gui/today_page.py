"""Today window for the Garum application."""

import flet as ft

from garum.gui.theme import ThemePalette


def build_today_page(
    palette: ThemePalette,
    on_settings: ft.ControlEventHandler,
) -> ft.Control:
    """Build the landing window with the settings action in its top-right corner."""
    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_OUTLINED,
                        selected_icon=ft.Icons.SETTINGS,
                        icon_color=palette.on_surface,
                        tooltip="Settings",
                        key="settings",
                        on_click=on_settings,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Today", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Your meals, nutrition, and spending for today.",
                            color=palette.muted,
                        ),
                    ],
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
        ],
    )
