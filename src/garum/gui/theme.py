"""Shared Garum color palettes, Flet theme builders and utility functions."""

from dataclasses import dataclass

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

THEME_PALETTES = {
    LIGHT_PALETTE.name: LIGHT_PALETTE,
    DARK_PALETTE.name: DARK_PALETTE,
}

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
        on_surface=palette.on_surface,
        on_surface_variant=palette.on_surface,
        outline=palette.border,
        error=palette.error,
        on_error="#FFFFFF",
    )
    appbar_theme = ft.AppBarTheme(
        color=palette.sidebar_text,
        bgcolor=palette.appbar,
        title_text_style=ft.TextStyle(color=palette.sidebar_text),
        toolbar_text_style=ft.TextStyle(color=palette.sidebar_text),
    )
    navigation_drawer_theme = ft.NavigationDrawerTheme(
        bgcolor=palette.appbar,
        indicator_color=palette.primary,
        label_text_style={
            ft.ControlState.DEFAULT: ft.TextStyle(color=palette.sidebar_text),
            ft.ControlState.SELECTED: ft.TextStyle(color=palette.sidebar_text),
        },
        icon_theme={
            ft.ControlState.DEFAULT: ft.IconTheme(color=palette.sidebar_text),
            ft.ControlState.SELECTED: ft.IconTheme(color=palette.sidebar_text),
        },
    )
    return ft.Theme(
        color_scheme=colors,
        appbar_theme=appbar_theme,
        navigation_drawer_theme=navigation_drawer_theme,
        use_material3=True,
    )
