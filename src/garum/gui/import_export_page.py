"""Import and export page for the application."""

from collections.abc import Callable

import flet as ft

from garum.gui.theme import ThemePalette


def update_import_export(action: str) -> None:
    """Print an import/export action until file handling is implemented."""
    print(f"Mock import/export action: {action}")


def build_import_export_page(
    palette: ThemePalette,
    on_close: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """Build the standalone import/export page."""
    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=palette.on_surface,
                        tooltip="Close import and export",
                        on_click=on_close,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.FilledButton(
                            "Import",
                            icon=ft.Icons.FILE_UPLOAD,
                            on_click=lambda _: update_import_export("import"),
                        ),
                        ft.FilledButton(
                            "Export",
                            icon=ft.Icons.FILE_DOWNLOAD,
                            on_click=lambda _: update_import_export("export"),
                        ),
                    ],
                    spacing=16,
                ),
                alignment=ft.Alignment.TOP_CENTER,
                padding=24,
                expand=True,
            ),
        ],
    )
