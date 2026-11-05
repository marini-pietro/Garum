"""Price and nutrition analytics window for the Garum application."""

import flet as ft

from garum.gui.theme import ThemePalette


def build_analytics_page(palette: ThemePalette) -> ft.Control:
    """Build the price and nutrition analytics landing window."""
    return ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Price & Nutrition Analytics", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Review spending and nutrition trends over time.",
                    color=palette.muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=24,
    )
