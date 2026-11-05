"""
Shared color palettes, Flet theme builders and utility functions.
"""

# First-party imports
from dataclasses import dataclass

# Third-party imports
import flet as ft


# dataclass decorator is used to automatically generate
# special methods for the class, such as __init__, __repr__, and __eq__.
# frozen=True makes the class immutable, meaning that its attributes cannot be modified after creation.
@dataclass(frozen=True)
class ThemePalette:
    name: str
    background: str
    surface: str
    surface_variant: str
    primary: str
    error: str
    on_surface: str
    muted: str
    border: str
    appbar: str
    sidebar_text: str
    icon_surface: str
    hero_gradient: tuple[str, str, str]


# Define light theme palette for the application.
LIGHT_PALETTE = ThemePalette(
    name="light",
    background="#E8D3B0",
    surface="#FFF8EE",
    surface_variant="#F5E8D3",
    primary="#A85D2A",
    error="#C62828",
    on_surface="#3D281A",
    muted="#795B43",
    border="#D4B88F",
    appbar="#8A4F2A",
    sidebar_text="#F8EBDD",
    icon_surface="#F7E8D1",
    hero_gradient=("#6F3E24", "#A85D2A", "#C98545"),
)

# Define dark theme palette for the application.
DARK_PALETTE = ThemePalette(
    name="dark",
    background="#3A3A3A",
    surface="#000000",
    surface_variant="#4A4A4A",
    primary="#D6D6D6",
    error="#C62828",
    on_surface="#FFFFFF",
    muted="#D0D0D0",
    border="#666666",
    appbar="#000000",
    sidebar_text="#FFFFFF",
    icon_surface="#5A5A5A",
    hero_gradient=("#161616", "#303030", "#555555"),
)

# Define a dictionary that maps theme names to their corresponding ThemePalette instances.
THEME_PALETTES = {
    LIGHT_PALETTE.name: LIGHT_PALETTE,
    DARK_PALETTE.name: DARK_PALETTE,
}

# Define a global variable to hold the currently active theme palette.
active_palette: ThemePalette = LIGHT_PALETTE


def get_palette(theme_name: str) -> ThemePalette:
    """Return the configured palette, or raise for an unsupported theme."""
    try:
        return THEME_PALETTES[theme_name]
    except KeyError as error:
        raise ValueError(f"Unknown theme: {theme_name}") from error


def set_active_palette(theme_name: str) -> ThemePalette:
    """Set and return the palette used by reusable UI builders."""
    global active_palette
    active_palette = get_palette(theme_name)
    return active_palette


def build_theme(palette: ThemePalette) -> ft.Theme:
    """Build a Material 3 theme from a named Garum palette."""
    colors = ft.ColorScheme(
        primary=palette.primary,
        on_primary=palette.on_surface,
        secondary=palette.primary,
        on_secondary=palette.on_surface,
        surface=palette.surface,
        surface_container=palette.surface_variant,
        surface_container_high=palette.surface_variant,
        surface_container_low=palette.surface,
        on_surface=palette.on_surface,
        on_surface_variant=palette.on_surface,
        outline=palette.border,
        error=palette.error,
        on_error="#FFFFFF",
    )
    return ft.Theme(
        color_scheme=colors,
        use_material3=True,
    )
