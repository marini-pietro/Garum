"""Catalogue and inventory window for the Garum application."""

import flet as ft

from garum.gui.theme import ThemePalette


def build_catalogue_page(palette: ThemePalette) -> ft.Control:
    """Build the catalogue and inventory landing window."""
    return ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Catalogue & Inventory", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Manage known products and the quantities currently available.",
                    color=palette.muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=24,
    )
