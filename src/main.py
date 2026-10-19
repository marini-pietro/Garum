# First party imports
from settings_page import show_settings
from settings_handler import load_settings, settings
from theme_handler import DARK_PALETTE, LIGHT_PALETTE, build_theme, set_active_palette

# Library imports
import flet as ft

def show_home(e: ft.Event[ft.TextButton]):
    page = e.page
    page.dialog = ft.AlertDialog(
        title=ft.Text("Home"),
        content=ft.Text("Home dialog content goes here."),
        actions=[
            ft.TextButton("Close", on_click=lambda e: page.dialog.close())
        ],
    )
    page.dialog.open = True
    page.update()

def main(page: ft.Page):

    async def open_drawer(e):
        await page.show_drawer()

    # Set appearence of the page
    page.title = "Garum" # Set the title of the page
    page.theme = build_theme(LIGHT_PALETTE) # Build the color palette for the light theme
    page.dark_theme = build_theme(DARK_PALETTE) # Build the color palette for the dark theme
    page.theme_mode = ft.ThemeMode.DARK if chosen_theme == "dark" else ft.ThemeMode.LIGHT

    # Set the navigation drawer of the page
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

    # Set the app bar of the page
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
            )
        ],
    )


if __name__ == "__main__":
    load_settings() # Load the settings from the settings file
    chosen_theme = settings["APP_THEME"] # Load the chosen theme from settings
    palette = set_active_palette(str(chosen_theme)) # Set the active palette based on the chosen theme
    ft.run(main)
