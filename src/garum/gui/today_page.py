"""Today page for the Garum application."""

# Third party imports
import flet as ft

# Local imports
from garum.handlers.analytics_handler import AnalyticsHandler
from garum.gui.theme import ThemePalette


def build_today_page(
    palette: ThemePalette,
    on_settings: ft.ControlEventHandler,
    on_import_export: ft.ControlEventHandler,
    analytics: AnalyticsHandler | None = None,
) -> ft.Control:
    """
    Build today page's widgets with the settings action in the top-right corner.
    """

    # Get today's macronutrient amounts and corresponding nutrient objects
    macro_amounts = (
        {
            code: amount
            for code, amount in analytics.calculate_daily_macronutrient_amounts().items()
            if code != "kcals"
        }
        if analytics is not None
        else {}
    )
    macro_nutrients = (
        {
            nutrient.code: nutrient
            for nutrient in analytics.storage.nutrients.list(limit=100)
            if nutrient.code in macro_amounts
        }
        if analytics is not None
        else {}
    )
    macro_bars = [
        ft.Column(
            width=82,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(
                    code.replace("_", " ").title(),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    width=28,
                    height=140,
                    bgcolor=palette.surface_variant,
                    border_radius=9,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Stack(
                        width=28,
                        height=140,
                        alignment=ft.Alignment.BOTTOM_CENTER,
                        controls=[
                            ft.Container(
                                width=28,
                                height=140
                                * min(
                                    amount / analytics.daily_reference_values[code],
                                    1,
                                ),
                                bgcolor=palette.primary,
                                border_radius=9,
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    f"{amount}{macro_nutrients[code].unit} / "
                    f"{analytics.daily_reference_values[code]:g}"
                    f"{macro_nutrients[code].unit}",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        )
        for code, amount in macro_amounts.items()
    ]

    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.IMPORT_EXPORT_ROUNDED,
                        icon_color=palette.on_surface,
                        key="import_export",
                        on_click=on_import_export,
                        padding=16,
                        icon_size=32,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        selected_icon=ft.Icons.SETTINGS,
                        icon_color=palette.on_surface,
                        key="settings",
                        on_click=on_settings,
                        padding=16,
                        icon_size=32,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=macro_bars,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                                wrap=True,
                            ),
                            width=500,
                            padding=20,
                            bgcolor=palette.surface,
                            border_radius=12,
                        ),
                    ],
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
        ],
    )
