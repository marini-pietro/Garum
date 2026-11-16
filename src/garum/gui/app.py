"""Primary Flet page for the Garum application."""

# Third party imports
import flet as ft

# First party imports
from collections.abc import Callable

# Local imports
from garum.gui.analytics_page import build_analytics_page
from garum.gui.catalogue_page import (
    add_food,
    build_catalogue_page,
)
from garum.gui.food_details_page import build_food_detail_page
from garum.gui.today_page import build_today_page
from garum.gui.settings_page import build_settings_page
from garum.gui.services import GuiServices
from garum.gui.import_export_page import build_import_export_page
from garum.gui.theme import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    build_theme,
    set_active_palette,
)
from garum.handlers.analytics_handler import AnalyticsHandler
from garum.handlers.models import Food
from garum.handlers.settings_handler import load_settings, settings
from garum.handlers.storage_handler import StorageHandler


def create_landing_page(services: GuiServices) -> Callable[[ft.Page], None]:
    """Create the Flet page callback with its shared services."""

    def landing_page(page: ft.Page) -> None:
        """Configure the Garum page and its navigation controls."""

        # Set the active palette based on the current theme in settings
        palette = set_active_palette(str(settings["APP_THEME"]))

        # Configure the page
        page.title = "Garum"
        # No need to set up the page icon as during the build command flet will automatically pick up the assets/icon.png file
        page.bgcolor = palette.background
        page.padding = 0
        page.spacing = 0
        page.theme = build_theme(LIGHT_PALETTE)
        page.dark_theme = build_theme(DARK_PALETTE)
        page.theme_mode = (
            ft.ThemeMode.DARK if settings["APP_THEME"] == "dark" else ft.ThemeMode.LIGHT
        )

        # Create a container with the output of the first page as its content and set it to expand to fill the available space
        content = ft.Container(expand=True)
        selected_index = 0

        def close_settings(_: ft.ControlEvent) -> None:
            """Return to the page that opened settings."""
            content.content = destinations[selected_index]
            navigation_bar.visible = True
            page.update()

        def open_settings(_: ft.ControlEvent) -> None:
            """Display settings as a standalone page."""
            content.content = build_settings_page(palette, settings, close_settings)
            navigation_bar.visible = False
            page.update()

        def close_import_export(_: ft.ControlEvent) -> None:
            """Return to the page that opened import/export."""
            content.content = destinations[selected_index]
            navigation_bar.visible = True
            page.update()

        def open_import_export(_: ft.ControlEvent) -> None:
            """Display import/export as a standalone page."""
            content.content = build_import_export_page(palette, close_import_export)
            navigation_bar.visible = False
            page.update()

        def close_food_detail(_: ft.ControlEvent) -> None:
            """Return to the catalogue after viewing food details."""
            content.content = destinations[selected_index]
            navigation_bar.visible = True
            page.update()

        def open_food_detail(food: Food) -> None:
            """Display nutritional information for a selected food."""
            content.content = build_food_detail_page(
                palette, services.storage, food, close_food_detail
            )
            navigation_bar.visible = False
            page.update()

        def close_add_food(_: ft.ControlEvent) -> None:
            """Return to the refreshed catalogue after adding a food."""
            destinations[selected_index] = build_catalogue_page(
                palette,
                services.storage,
                open_food_detail,
                open_add_food,
            )
            content.content = destinations[selected_index]
            navigation_bar.visible = True
            page.update()

        def open_add_food() -> None:
            """Display the form used to add a food."""
            content.content = add_food(palette, services.storage, close_add_food)
            navigation_bar.visible = False
            page.update()

        def select_page(event: ft.ControlEvent) -> None:
            """Display the page selected in the bottom navigation bar."""
            nonlocal selected_index
            selected_index = event.control.selected_index
            content.content = destinations[event.control.selected_index]
            page.update()

        # Create an array of the three pages reachable by the bottom navigation bar
        destinations = [
            build_today_page(
                palette, open_settings, open_import_export, services.analytics
            ),
            build_catalogue_page(
                palette,
                services.storage,
                open_food_detail,
                open_add_food,
            ),
            build_analytics_page(palette),
        ]
        content.content = destinations[0]

        navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=select_page,
            height=64,  # Set the height of the navigation bar to 64 pixels
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_HIDE,  # Hide labels for a cleaner look (even if labels are not given they will be an empty string)
            label_padding=0,  # Remove padding around labels for a cleaner look
            bgcolor=palette.surface,
            indicator_color=palette.icon_surface,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.TODAY_OUTLINED,
                    selected_icon=ft.Icons.TODAY,
                    key="today_page",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    selected_icon=ft.Icons.INVENTORY_2,
                    key="catalogue_page",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.AREA_CHART_OUTLINED,
                    selected_icon=ft.Icons.AREA_CHART,
                    key="analytics_page",
                ),
            ],
        )

        # Add the content and navigation bar to the page
        page.add(
            content,
            navigation_bar,
        )

    return landing_page


def main() -> None:
    """Load preferences and start the Flet application."""

    # Load user settings and get a reference to them
    user_settings = load_settings()

    # Get a reference to the storage handler and create the services object which is then passed among the GUI pages
    storage = StorageHandler.get_reference()
    services = GuiServices(
        storage=storage, analytics=AnalyticsHandler(storage, user_settings)
    )

    # Run the Flet application with the landing page callback and the services object
    ft.run(create_landing_page(services))
