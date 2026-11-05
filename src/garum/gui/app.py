"""Primary Flet page for the Garum application."""

import flet as ft

from garum.gui.analytics_page import build_analytics_page
from garum.gui.catalogue_page import build_catalogue_page
from garum.gui.settings_page import show_settings
from garum.gui.today_page import build_today_page
from garum.gui.theme import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    build_theme,
    set_active_palette,
)
from garum.handlers.settings_handler import load_settings, settings


def main_page(page: ft.Page) -> None:
    """Configure the Garum page and its navigation controls."""
    palette = set_active_palette(str(settings["APP_THEME"]))

    page.title = "Garum"
    page.bgcolor = palette.background
    page.padding = 0
    page.theme = build_theme(LIGHT_PALETTE)
    page.dark_theme = build_theme(DARK_PALETTE)
    page.theme_mode = (
        ft.ThemeMode.DARK if settings["APP_THEME"] == "dark" else ft.ThemeMode.LIGHT
    )

    destinations = [
        build_today_page(palette, show_settings),
        build_catalogue_page(palette),
        build_analytics_page(palette),
    ]
    content = ft.Container(content=destinations[0], expand=True)

    def select_page(event: ft.ControlEvent) -> None:
        """Display the page selected in the bottom navigation bar."""
        content.content = destinations[event.control.selected_index]
        page.update()

    page.add(
        content,
        ft.NavigationBar(
            selected_index=0,
            on_change=select_page,
            bgcolor=palette.surface,
            indicator_color=palette.primary,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.TODAY_OUTLINED,
                    selected_icon=ft.Icons.TODAY,
                    label="Today",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    selected_icon=ft.Icons.INVENTORY_2,
                    label="Catalogue",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.INSERT_CHART_OUTLINED,
                    selected_icon=ft.Icons.INSERT_CHART,
                    label="Analytics",
                ),
            ],
        ),
    )


def main() -> None:
    """Load preferences and start the Flet application."""
    load_settings()
    ft.run(main_page)
