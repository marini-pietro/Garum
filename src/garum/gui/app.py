"""Primary Flet page for the Garum application."""

# Third party imports
import flet as ft

# First party imports
from collections.abc import Callable

# Local imports
from garum.gui.analytics_page import build_analytics_page
from garum.gui.catalogue_page import build_catalogue_page
from garum.gui.services import GuiServices
from garum.gui.settings_page import show_settings
from garum.gui.today_page import build_today_page
from garum.gui.theme import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    build_theme,
    set_active_palette,
)
from garum.handlers.analytics_handler import AnalyticsHandler
from garum.handlers.settings_handler import load_settings, settings
from garum.handlers.storage_handler import StorageHandler


def create_landing_page(services: GuiServices) -> Callable[[ft.Page], None]:
    """Create the Flet page callback with its shared services."""

    def landing_page(page: ft.Page) -> None:
        """Configure the Garum page and its navigation controls."""

        # Set the active palette based on the current theme in settings
        palette = set_active_palette(str(settings["APP_THEME"]))

        # Configure the page with its title, background color, padding, and theme
        page.title = "Garum"
        page.bgcolor = palette.background
        page.padding = 0
        page.spacing = 0
        page.theme = build_theme(LIGHT_PALETTE)
        page.dark_theme = build_theme(DARK_PALETTE)
        page.theme_mode = (
            ft.ThemeMode.DARK if settings["APP_THEME"] == "dark" else ft.ThemeMode.LIGHT
        )

        # Create an array of the three pages reachable by the bottom navigation bar
        destinations = [
            build_today_page(palette, show_settings),
            build_catalogue_page(palette),
            build_analytics_page(palette),
        ]

        # Create a container with the output of the first page as its content and set it to expand to fill the available space
        content = ft.Container(content=destinations[0], expand=True)

        def select_page(event: ft.ControlEvent) -> None:
            """Display the page selected in the bottom navigation bar."""
            content.content = destinations[event.control.selected_index]
            page.update()

        # Add the content and navigation bar to the page
        page.add(
            content,
            ft.NavigationBar(
                selected_index=0,
                on_change=select_page,
                height=64, # Set the height of the navigation bar to 64 pixels
                label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_HIDE, # Hide labels for a cleaner look (even if labels are not given they will be an empty string)
                label_padding=0, # Remove padding around labels for a cleaner look
                bgcolor=palette.surface,
                indicator_color=palette.icon_surface,
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.Icons.TODAY_OUTLINED,
                        selected_icon=ft.Icons.TODAY,
                        key="today_page"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.INVENTORY_2_OUTLINED,
                        selected_icon=ft.Icons.INVENTORY_2,
                        key="catalogue_page"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.AREA_CHART_OUTLINED,
                        selected_icon=ft.Icons.AREA_CHART,
                        key="analytics_page"
                    ),
                ],
            ),
        )

    return landing_page


def main() -> None:
    """Load preferences and start the Flet application."""

    # Load user settings and get a reference to them
    user_settings = load_settings()

    # Get a reference to the storage handler and create the services object which is then passed among the GUI pages
    storage = StorageHandler.get_reference()
    services = GuiServices(
        storage=storage,
        analytics=AnalyticsHandler(storage, user_settings)
    )

    # Run the Flet application with the landing page callback and the services object
    ft.run(create_landing_page(services))
