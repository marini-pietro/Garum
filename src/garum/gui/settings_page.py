"""Settings dialog for the Garum application."""

import flet as ft


def show_settings(event: ft.ControlEvent) -> None:
    """Display the settings dialog."""
    page = event.page
    page.dialog = ft.AlertDialog(
        title=ft.Text("Settings"),
        content=ft.Text("Settings dialog content goes here."),
        actions=[
            ft.TextButton("Close", on_click=lambda _: page.close_dialog()),
        ],
    )
    page.open(page.dialog)
