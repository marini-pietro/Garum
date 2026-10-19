from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import flet as ft

from garum.models import MealEntry
from garum.settings_handler import load_settings
from garum.storage import MealEntryStore
from garum import theme


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT
DATABASE_PATH = Path.home() / ".garum" / "garum.sqlite3"
STORE = MealEntryStore(DATABASE_PATH)


@dataclass(frozen=True)
class NutritionSnapshot:
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    spend: float
    streak_days: int


SNAPSHOT = NutritionSnapshot(0, 0, 0, 0, 0.0, 0)
RECENT_ENTRIES: list[tuple[str, str, str, str]] = []

SEED_ENTRIES = [
    MealEntry(None, date.today() - timedelta(days=0), "Lunch: lentil bowl", 540, 4.80, 26, 66, 14),
    MealEntry(None, date.today() - timedelta(days=1), "Snack: yogurt and fruit", 220, 2.10, 12, 28, 4),
    MealEntry(None, date.today() - timedelta(days=2), "Dinner: pasta with vegetables", 680, 5.40, 24, 84, 18),
    MealEntry(None, date.today() - timedelta(days=3), "Breakfast: oats and peanut butter", 400, 3.10, 15, 45, 13),
    MealEntry(None, date.today() - timedelta(days=4), "Lunch: rice and tofu", 610, 4.95, 28, 71, 17),
    MealEntry(None, date.today() - timedelta(days=5), "Dinner: beans and roasted potatoes", 590, 5.25, 21, 74, 16),
    MealEntry(None, date.today() - timedelta(days=6), "Snack: apple and nuts", 250, 1.80, 6, 20, 17),
    MealEntry(None, date.today() - timedelta(days=7), "Lunch: chickpea wrap", 520, 4.40, 20, 61, 15),
    MealEntry(None, date.today() - timedelta(days=8), "Dinner: vegetable curry", 660, 6.20, 18, 82, 24),
    MealEntry(None, date.today() - timedelta(days=9), "Breakfast: eggs and toast", 430, 3.20, 24, 31, 22),
    MealEntry(None, date.today() - timedelta(days=10), "Lunch: quinoa salad", 480, 4.10, 17, 58, 15),
    MealEntry(None, date.today() - timedelta(days=11), "Dinner: salmon and greens", 720, 7.80, 42, 35, 33),
]

NAV_ITEMS = [
    ("Dashboard", ft.Icons.DASHBOARD_OUTLINED),
    ("Food log", ft.Icons.RESTAURANT_MENU),
    ("Insights", ft.Icons.QUERY_STATS_OUTLINED),
    ("Backups", ft.Icons.CLOUD_DONE_OUTLINED),
    ("Settings", ft.Icons.SETTINGS_OUTLINED),
]


def _refresh_persistent_state() -> None:
    global SNAPSHOT, RECENT_ENTRIES

    entries = STORE.list_entries(limit=100)
    if not entries:
        STORE.seed_if_empty(SEED_ENTRIES)
        entries = STORE.list_entries(limit=100)

    SNAPSHOT = _build_snapshot(entries)
    RECENT_ENTRIES = [_entry_summary(entry) for entry in entries[:4]]


def _build_snapshot(entries: list[MealEntry]) -> NutritionSnapshot:
    today = date.today()
    todays_entries = [entry for entry in entries if entry.occurred_on == today]

    def _sum(attribute: str) -> int:
        return int(sum(getattr(entry, attribute) for entry in todays_entries))

    streak = 0
    active_dates = {entry.occurred_on for entry in entries}
    cursor = today
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return NutritionSnapshot(
        calories=_sum("calories_kcal"),
        protein_g=_sum("protein_g"),
        carbs_g=_sum("carbs_g"),
        fat_g=_sum("fat_g"),
        spend=round(sum(entry.spend_usd for entry in todays_entries), 2),
        streak_days=streak,
    )


def _entry_summary(entry: MealEntry) -> tuple[str, str, str, str]:
    if entry.occurred_on == date.today():
        date_label = "Today"
    elif entry.occurred_on == date.today() - timedelta(days=1):
        date_label = "Yesterday"
    else:
        date_label = entry.occurred_on.strftime("%d %b")

    return (
        date_label,
        entry.meal,
        f"{entry.calories_kcal} kcal",
        f"${entry.spend_usd:.2f}",
    )


def _surface_container(content: ft.Control, *, padding: int = 20) -> ft.Container:
    palette = theme.active_palette
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=24,
        bgcolor=palette.surface,
        border=ft.border.all(1, palette.border),
    )


def _stat_card(title: str, value: str, detail: str, icon: str, tint: str) -> ft.Container:
    palette = theme.active_palette
    return _surface_container(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=14,
                            alignment=ft.alignment.center,
                            bgcolor=tint,
                            content=ft.Icon(icon, color=ft.Colors.WHITE),
                        ),
                        ft.Text(title, size=12, color=palette.muted, weight=ft.FontWeight.W_600),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(value, size=30, weight=ft.FontWeight.BOLD, color=palette.on_surface),
                ft.Text(detail, size=12, color=palette.muted),
            ],
            spacing=10,
        ),
        padding=18,
    )


def _progress_card(title: str, value: float, target_label: str, tint: str) -> ft.Container:
    palette = theme.active_palette
    percent = max(0.0, min(value, 1.0))
    return _surface_container(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(title, size=15, weight=ft.FontWeight.W_700),
                        ft.Text(f"{int(percent * 100)}%", size=13, color=palette.muted),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.ProgressBar(value=percent, color=tint, bgcolor=palette.surface_variant),
                ft.Text(target_label, size=12, color=palette.muted),
            ],
            spacing=10,
        ),
        padding=18,
    )


def _entry_row(date_label: str, meal: str, calories: str, spend: str) -> ft.Container:
    palette = theme.active_palette
    return ft.Container(
        padding=14,
        border_radius=18,
        bgcolor=palette.surface_variant,
        border=ft.border.all(1, palette.border),
        content=ft.Row(
            [
                ft.Container(width=12, height=12, border_radius=6, bgcolor="#A87432"),
                ft.Column(
                    [
                        ft.Text(date_label, size=12, color=palette.muted),
                        ft.Text(meal, size=14, weight=ft.FontWeight.W_600, color=palette.on_surface),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Text(calories, size=13, weight=ft.FontWeight.W_600, color=palette.on_surface),
                        ft.Text(spend, size=12, color="#7A7266"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )


def _hero_section() -> ft.Container:
    palette = theme.active_palette
    return ft.Container(
        padding=24,
        border_radius=32,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=palette.hero_gradient,
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=64,
                            height=64,
                            border_radius=18,
                            bgcolor=palette.icon_surface,
                            alignment=ft.alignment.center,
                            content=ft.Image(
                                src="logo/garum_logo_complete.svg",
                                width=40,
                                height=40,
                                fit=ft.BoxFit.CONTAIN,
                                semantics_label="Garum logo",
                            ),
                        ),
                        ft.Column(
                            [
                                ft.Text("Garum", size=34, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(
                                    "Track nutrition, spending, and trend signals without making the workflow heavy.",
                                    size=14,
                                    color="#E9E1D2",
                                ),
                            ],
                            spacing=6,
                            expand=True,
                        ),
                    ],
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        _stat_card(
                            "Calories",
                            f"{SNAPSHOT.calories}",
                            "Logged today",
                            ft.Icons.FLAME_OUTLINED,
                            "#5E8A54",
                        ),
                        _stat_card(
                            "Protein",
                            f"{SNAPSHOT.protein_g} g",
                            "Towards daily target",
                            ft.Icons.FITNESS_CENTER_OUTLINED,
                            "#8C6A2D",
                        ),
                        _stat_card(
                            "Spend",
                            f"${SNAPSHOT.spend:.2f}",
                            "Food budget today",
                            ft.Icons.ATTACH_MONEY_OUTLINED,
                            "#6B7D8A",
                        ),
                    ],
                    wrap=True,
                    spacing=16,
                    run_spacing=16,
                ),
            ],
            spacing=18,
        ),
    )


def _dashboard_view() -> ft.Control:
    return ft.ListView(
        expand=True,
        spacing=18,
        padding=24,
        controls=[
            _hero_section(),
            ft.Row(
                [
                    ft.Container(
                        expand=2,
                        content=_surface_container(
                            ft.Column(
                                [
                                    ft.Text("Macronutrient balance", size=16, weight=ft.FontWeight.W_700),
                                    _progress_card("Protein", 0.64, "96 g of 150 g", "#6E9F57"),
                                    _progress_card("Carbohydrates", 0.73, "221 g of 300 g", "#A8792E"),
                                    _progress_card("Fat", 0.58, "58 g of 100 g", "#647C85"),
                                ],
                                spacing=14,
                            )
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=_surface_container(
                            ft.Column(
                                [
                                    ft.Text("Momentum", size=16, weight=ft.FontWeight.W_700),
                                    ft.Text(
                                        f"{SNAPSHOT.streak_days} day tracking streak",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Keep the daily log clean and the trend lines will stay useful.",
                                        size=13,
                                        color=theme.active_palette.muted,
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
            ft.Row(
                [
                    ft.Container(
                        expand=1,
                        content=_surface_container(
                            ft.Column(
                                [
                                    ft.Text("Recent entries", size=16, weight=ft.FontWeight.W_700),
                                    *[_entry_row(*entry) for entry in RECENT_ENTRIES],
                                ],
                                spacing=12,
                            )
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=_surface_container(
                            ft.Column(
                                [
                                    ft.Text("Next boilerplate", size=16, weight=ft.FontWeight.W_700),
                                    ft.Text(
                                        "This section is ready for graph widgets, synced data sources, and filters.",
                                        size=13,
                                        color="#7A7266",
                                    ),
                                    ft.Container(height=12),
                                    ft.Container(
                                        padding=18,
                                        border_radius=18,
                                        bgcolor=theme.active_palette.surface_variant,
                                        content=ft.Column(
                                            [
                                                ft.Text("Planned modules", size=13, weight=ft.FontWeight.W_600),
                                                ft.Text("- food logging and editing"),
                                                ft.Text("- nutrition evaluation presets"),
                                                ft.Text("- charting over time spans"),
                                                ft.Text("- encrypted Google Drive sync"),
                                            ],
                                            spacing=4,
                                        ),
                                    ),
                                ],
                                spacing=12,
                            )
                        ),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
        ],
    )


def _placeholder_view(title: str, body: str) -> ft.Control:
    return ft.Container(
        expand=True,
        padding=24,
        content=ft.Column(
            [
                ft.Text(title, size=28, weight=ft.FontWeight.BOLD),
                ft.Text(body, size=14, color="#6A6255"),
                ft.Container(height=16),
                _surface_container(
                    ft.Column(
                        [
                            ft.Text("Boilerplate area", size=16, weight=ft.FontWeight.W_700),
                            ft.Text(
                                "This page is intentionally sparse for now and ready for the real implementation.",
                                size=13,
                                color="#7A7266",
                            ),
                        ],
                        spacing=8,
                    )
                ),
            ],
            spacing=12,
        ),
    )


class FoodLogPanel:
    def __init__(self, shell: "GarumShell") -> None:
        self.shell = shell
        self.date_field = ft.TextField(label="Date", hint_text="YYYY-MM-DD", width=180, value=date.today().isoformat())
        self.meal_field = ft.TextField(label="Meal", hint_text="Lunch: lentil bowl", expand=True)
        self.calories_field = ft.TextField(label="Calories", hint_text="540", width=130)
        self.spend_field = ft.TextField(label="Spend", hint_text="4.80", width=130)
        self.protein_field = ft.TextField(label="Protein g", hint_text="26", width=130)
        self.carbs_field = ft.TextField(label="Carbs g", hint_text="66", width=130)
        self.fat_field = ft.TextField(label="Fat g", hint_text="14", width=130)
        self.notes_field = ft.TextField(label="Notes", multiline=True, min_lines=3, max_lines=5, expand=True)
        self.entries_list = ft.Column(spacing=10)

    def build(self) -> ft.Control:
        self.refresh()
        return ft.ListView(
            expand=True,
            spacing=18,
            padding=24,
            controls=[
                ft.Text("Food log", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Capture meals locally with SQLite and keep the dashboard in sync with the latest entries.",
                    size=14,
                    color="#6A6255",
                ),
                _surface_container(
                    ft.Column(
                        [
                            ft.Text("Add entry", size=16, weight=ft.FontWeight.W_700),
                            ft.Row([self.date_field, self.calories_field, self.spend_field], spacing=12, wrap=True),
                            ft.Row([self.meal_field], spacing=12),
                            ft.Row([self.protein_field, self.carbs_field, self.fat_field], spacing=12, wrap=True),
                            self.notes_field,
                            ft.Row(
                                [
                                    ft.FilledButton("Save entry", on_click=self.save_entry),
                                    ft.TextButton("Reload", on_click=self.reload_entries),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        spacing=12,
                    )
                ),
                _surface_container(
                    ft.Column(
                        [
                            ft.Text("Stored entries", size=16, weight=ft.FontWeight.W_700),
                            self.entries_list,
                        ],
                        spacing=12,
                    )
                ),
            ],
        )

    def refresh(self) -> None:
        self.entries_list.controls = [_entry_row(*_entry_summary(entry)) for entry in self.shell.entries[:12]]

    def reload_entries(self, _event: ft.ControlEvent) -> None:
        self.shell.reload_data()
        self.refresh()
        self.shell.page.update()

    def save_entry(self, _event: ft.ControlEvent) -> None:
        meal = (self.meal_field.value or "").strip()
        calories_text = (self.calories_field.value or "").strip()
        spend_text = (self.spend_field.value or "").strip()
        protein_text = (self.protein_field.value or "").strip()
        carbs_text = (self.carbs_field.value or "").strip()
        fat_text = (self.fat_field.value or "").strip()
        notes = (self.notes_field.value or "").strip()

        if not meal or not calories_text or not spend_text:
            return

        try:
            occurred_on = date.fromisoformat((self.date_field.value or date.today().isoformat()).strip())
            calories_kcal = int(calories_text)
            spend_usd = float(spend_text)
            protein_g = float(protein_text or 0)
            carbs_g = float(carbs_text or 0)
            fat_g = float(fat_text or 0)
        except ValueError:
            return

        STORE.add_entry(
            MealEntry(
                id=None,
                occurred_on=occurred_on,
                meal=meal,
                calories_kcal=calories_kcal,
                spend_usd=spend_usd,
                protein_g=protein_g,
                carbs_g=carbs_g,
                fat_g=fat_g,
                notes=notes,
            )
        )

        self.shell.reload_data()
        self.date_field.value = date.today().isoformat()
        self.meal_field.value = ""
        self.calories_field.value = ""
        self.spend_field.value = ""
        self.protein_field.value = ""
        self.carbs_field.value = ""
        self.fat_field.value = ""
        self.notes_field.value = ""
        self.refresh()
        self.shell.page.update()


class GarumShell:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.current_index = 0
        self.entries: list[MealEntry] = []
        self.snapshot = SNAPSHOT
        self.content_host = ft.Container(expand=True)
        self.food_log_panel = FoodLogPanel(self)
        self.navigation = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=88,
            min_extended_width=220,
            group_alignment=-0.95,
            on_change=self._on_navigation_change,
            destinations=[ft.NavigationRailDestination(icon=icon, label=label) for label, icon in NAV_ITEMS],
        )

    def reload_data(self) -> None:
        _refresh_persistent_state()
        self.entries = STORE.list_entries(limit=100)
        self.snapshot = SNAPSHOT

    def build(self) -> ft.Control:
        palette = theme.active_palette
        self.navigation.width = 96
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=(palette.background, palette.surface_variant, palette.border),
            ),
            content=ft.SafeArea(
                ft.Row(
                    [
                        ft.Container(
                            width=140,
                            padding=16,
                            bgcolor=palette.appbar,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(
                                                width=42,
                                                height=42,
                                                border_radius=14,
                                                bgcolor=palette.icon_surface,
                                                alignment=ft.alignment.center,
                                                content=ft.Image(
                                                    src="logo/garum_logo_complete.svg",
                                                    width=28,
                                                    height=28,
                                                    fit=ft.BoxFit.CONTAIN,
                                                    semantics_label="Garum logo",
                                                ),
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text("Garum", size=22, weight=ft.FontWeight.BOLD, color=palette.sidebar_text),
                                                    ft.Text("nutrition", size=12, color=palette.sidebar_text),
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=12,
                                    ),
                                ],
                                spacing=4,
                            ),
                        ),
                        ft.Container(width=1, bgcolor=palette.border),
                        ft.Container(width=116, padding=12, content=self.navigation),
                        ft.Container(width=1, bgcolor=palette.border),
                        ft.Container(expand=True, content=self.content_host),
                    ],
                    expand=True,
                    spacing=0,
                )
            ),
        )

    def show(self) -> None:
        self.reload_data()
        self.page.add(self.build())
        self._set_view(0)

    def _set_view(self, index: int) -> None:
        self.current_index = index
        title, _icon = NAV_ITEMS[index]
        if title == "Dashboard":
            content = _dashboard_view()
        elif title == "Food log":
            content = self.food_log_panel.build()
        elif title == "Insights":
            content = _placeholder_view(
                "Insights",
                "This view will host charts, macro breakdowns, and range selectors.",
            )
        elif title == "Backups":
            content = _placeholder_view(
                "Backups",
                "Use this area for encrypted sync status, restore points, and cloud connection details.",
            )
        else:
            content = _placeholder_view(
                "Settings",
                "Configuration for health presets, data sources, privacy, and app preferences goes here.",
            )

        self.content_host.content = content
        self.page.update()

    def _on_navigation_change(self, event: ft.ControlEvent) -> None:
        self._set_view(event.control.selected_index)


def main() -> None:
    ft.app(target=_run_app, assets_dir=str(ASSETS_DIR))


def _run_app(page: ft.Page) -> None:
    configured_theme = load_settings()["APP_THEME"]
    palette = theme.set_active_palette(configured_theme)
    page.title = "Garum"
    page.theme_mode = ft.ThemeMode.DARK if configured_theme == "dark" else ft.ThemeMode.LIGHT
    page.theme = theme.build_theme(theme.LIGHT_PALETTE)
    page.dark_theme = theme.build_theme(theme.DARK_PALETTE)
    page.padding = 0
    page.spacing = 0
    page.bgcolor = palette.background
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.icon = str(PROJECT_ROOT / "logo" / "garum_logo_complete.svg")

    GarumShell(page).show()
