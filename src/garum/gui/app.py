"""Primary Flet page for the Garum application."""

import flet as ft

from garum.gui.settings_page import show_settings
from garum.gui.theme import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    build_theme,
    set_active_palette,
)
from garum.handlers.settings_handler import load_settings, settings


def show_home(event: ft.ControlEvent) -> None:
    """Display the home dialog."""
    page = event.page
    page.dialog = ft.AlertDialog(
        title=ft.Text("Home"),
        content=ft.Text("Home dialog content goes here."),
        actions=[
            ft.TextButton("Close", on_click=lambda _: page.close_dialog()),
        ],
    )
    page.open(page.dialog)


async def open_drawer(event: ft.ControlEvent) -> None:
    """Open the navigation drawer associated with the current page."""
    await event.page.show_drawer()


def main_page(page: ft.Page) -> None:
    """Configure the Garum page and its navigation controls."""
    palette = set_active_palette(str(settings["APP_THEME"]))

    page.title = "Garum"
    page.theme = build_theme(LIGHT_PALETTE)
    page.dark_theme = build_theme(DARK_PALETTE)
    page.theme_mode = (
        ft.ThemeMode.DARK if settings["APP_THEME"] == "dark" else ft.ThemeMode.LIGHT
    )

    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.NavigationDrawerDestination(
                icon=ft.Icons.ARTICLE_ROUNDED,
                label="Inventory",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
                label="Calendar",
            ),
        ],
    )

    page.appbar = ft.AppBar(
        bgcolor=palette.appbar,
        elevation=6,
        shadow_color=palette.border,
        shape=ft.RoundedRectangleBorder(radius=32),
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=palette.sidebar_text,
            key="menu",
            on_click=open_drawer,
        ),
        title=ft.TextButton(
            content=ft.Text("Garum", color=palette.sidebar_text),
            style=ft.ButtonStyle(color=palette.sidebar_text),
            key="home_text",
            on_click=show_home,
        ),
        center_title=True,
        actions=[
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color=palette.sidebar_text,
                key="settings",
                on_click=show_settings,
            ),
        ],
    )


def main() -> None:
    """Load preferences and start the Flet application."""
    load_settings()
    ft.run(main_page)
