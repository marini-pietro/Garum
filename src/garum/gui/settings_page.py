"""Settings page for the application."""

# Third party imports
from collections.abc import Callable, Mapping

# Third party imports
import flet as ft

# Local imports
from garum.gui.theme import ThemePalette


def update_setting(key: str, value: str | bool) -> None:
    """Print a setting update until persistence is implemented."""
    print(f"Mock setting update: {key}={value}")


def build_settings_page(
    palette: ThemePalette,
    current_settings: Mapping[str, str | int | float],
    on_close: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """Build the standalone settings page."""
    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=palette.on_surface,
                        tooltip="Close settings",
                        on_click=on_close,
                        padding=16,
                        icon_size=32,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Dropdown(
                            label="Language",
                            value=str(current_settings["APP_LANGUAGE"]),
                            options=[
                                ft.DropdownOption(key="en", text="English"),
                                ft.DropdownOption(key="it", text="Italian"),
                            ],
                            on_select=lambda event: update_setting(
                                "APP_LANGUAGE", event.control.value
                            ),
                        ),
                        ft.Dropdown(
                            label="Theme",
                            value=str(current_settings["APP_THEME"]),
                            options=[
                                ft.DropdownOption(key="light", text="Light"),
                                ft.DropdownOption(key="dark", text="Dark"),
                            ],
                            on_select=lambda event: update_setting(
                                "APP_THEME", event.control.value
                            ),
                        ),
                        ft.Dropdown(
                            label="Measurement system",
                            value=str(current_settings["MEASUREMENT_SYSTEM"]),
                            options=[
                                ft.DropdownOption(key="metric", text="Metric"),
                            ],
                            on_select=lambda event: update_setting(
                                "MEASUREMENT_SYSTEM", event.control.value
                            ),
                        ),
                        ft.Switch(
                            label="Enable advertisements",
                            value=bool(current_settings["ENABLE_ADVERTISEMENTS"]),
                            on_change=lambda event: update_setting(
                                "ENABLE_ADVERTISEMENTS", event.control.value
                            ),
                        ),
                    ],
                    spacing=16,
                ),
                alignment=ft.Alignment.TOP_CENTER,
                padding=24,
                expand=True,
            ),
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Image(
                                src="src\\assets\\github_logo_white.svg",
                                width=96,
                                height=96,
                            ),
                            url="https://github.com/marini-pietro/Garum",
                            padding=16,
                        ),
                    ],
                ),
                padding=ft.Padding.only(bottom=24),
            ),
        ],
    )
