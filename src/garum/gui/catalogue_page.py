"""Catalogue and food detail pages for the Garum application."""

# Standard library imports
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import sqlite3

# Third party imports
import flet as ft
from flet_datatable2 import DataColumn2, DataRow2, DataTable2

# Local imports
from garum.gui.theme import ThemePalette
from garum.gui.food_details_page import _load_food_detail_data, _build_food_detail_table
from garum.handlers.storage_handler import StorageHandler
from garum.handlers.models import (
    Brand,
    Category,
    Food,
    FoodCategory,
    FoodNutrient,
    FoodNutrientBase,
    Unit,
)

# Define limits for the number of records to load from the storage handler to
# prevent excessive memory usage and ensure responsive UI performance.
FOOD_LIMIT = 1000
CATEGORY_LIMIT = 1000
FOOD_CATEGORY_LIMIT = 5000
UNIT_LIMIT = 1000
INVENTORY_LIMIT = 5000
NUTRIENT_LIMIT = 1000
FOOD_BASE_LIMIT = 1000
FOOD_NUTRIENT_LIMIT = 5000


@dataclass(frozen=True)
class CatalogueData:
    """Prepared catalogue values used by the search and table controls."""

    foods: list[Food]
    category_names: dict[int, str]
    quantities: dict[int, list[str]]
    quantity_sort_values: dict[int, float]


def _load_catalogue_data(storage: StorageHandler | None) -> CatalogueData:
    """Load catalogue records and prepare values needed by the table."""

    if storage is None:
        return CatalogueData([], {}, {}, {})

    foods = storage.foods.list(limit=FOOD_LIMIT)
    categories = {
        category.id: category.name
        for category in storage.categories.list(limit=CATEGORY_LIMIT)
    }
    food_categories = storage.food_categories.list(limit=FOOD_CATEGORY_LIMIT)
    category_names = {
        food.id: ", ".join(
            sorted(
                categories[link.category_id]
                for link in food_categories
                if link.food_id == food.id and link.category_id in categories
            )
        )
        for food in foods
    }

    units = {unit.id: unit.code for unit in storage.units.list(limit=UNIT_LIMIT)}
    quantities: dict[int, list[str]] = {}
    quantity_sort_values: dict[int, float] = {}
    for item in storage.inventory.list(limit=INVENTORY_LIMIT):
        if item.food_id is None:
            continue

        quantity = f"{item.quantity:g} {units.get(item.unit_id, '')}".strip()
        quantities.setdefault(item.food_id, []).append(quantity)
        quantity_sort_values[item.food_id] = (
            quantity_sort_values.get(item.food_id, 0) + item.quantity
        )

    return CatalogueData(
        foods=foods,
        category_names=category_names,
        quantities=quantities,
        quantity_sort_values=quantity_sort_values,
    )


def _is_subsequence(query: str, candidate: str) -> bool:
    """Return whether all query characters occur in order in the candidate."""

    query_position = 0
    for character in candidate:
        if query_position < len(query) and character == query[query_position]:
            query_position += 1
    return query_position == len(query)


def _search_score(
    food: Food,
    query: str,
    category_names: dict[int, str],
) -> int | None:
    """Return a relevance score, or None when the food does not match."""

    candidates = (
        food.name.casefold(),
        category_names.get(food.id, "").casefold(),
    )
    best_score: int | None = None
    for candidate in candidates:
        if not candidate:
            continue

        if candidate == query:
            score = 0
        elif candidate.startswith(query):
            score = 1
        elif any(word.startswith(query) for word in candidate.split()):
            score = 2
        elif query in candidate:
            score = 3
        elif _is_subsequence(query, candidate):
            score = 4
        else:
            continue

        best_score = score if best_score is None else min(best_score, score)

    return best_score


def _sort_foods(
    foods: list[Food],
    data: CatalogueData,
    query: str,
    sort_key: str,
) -> list[Food]:
    """Filter foods by query and apply relevance and table sorting."""

    scored_foods: list[tuple[Food, int]] = []
    for food in foods:
        score = _search_score(food, query, data.category_names) if query else 0
        if score is not None:
            scored_foods.append((food, score))

    if sort_key == "categories":
        scored_foods.sort(
            key=lambda item: data.category_names.get(item[0].id, "").casefold()
        )
    elif sort_key == "quantity":
        scored_foods.sort(key=lambda item: data.quantity_sort_values.get(item[0].id, 0))
    else:
        scored_foods.sort(key=lambda item: item[0].name.casefold())

    # Relevance is the primary order during a search; the selected table
    # sort remains the stable tie-breaker.
    if query:
        scored_foods.sort(key=lambda item: item[1])

    return [food for food, _ in scored_foods]


def _build_catalogue_rows(
    foods: list[Food],
    data: CatalogueData,
    palette: ThemePalette,
    on_food_selected: Callable[[Food], None] | None,
) -> list[DataRow2]:
    """Build table rows for the currently filtered foods."""

    rows = []
    for food in foods:
        # Bind the selected food when creating each row, rather than when
        # the click callback eventually runs.
        def select_current_food(_: ft.ControlEvent, selected_food: Food = food) -> None:
            if on_food_selected is not None:
                on_food_selected(selected_food)

        rows.append(
            DataRow2(
                cells=[
                    ft.DataCell(
                        ft.TextButton(
                            food.name,
                            style=ft.ButtonStyle(color=palette.primary),
                            on_click=select_current_food,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            data.category_names.get(food.id, "—") or "—",
                            color=palette.on_surface,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            ", ".join(data.quantities.get(food.id, [])) or "—",
                            color=palette.on_surface,
                        )
                    ),
                ]
            )
        )
    return rows


def _build_catalogue_table(
    rows: list[DataRow2],
    palette: ThemePalette,
) -> DataTable2:
    """Build the catalogue table with the application's shared styling."""

    return DataTable2(
        columns=[
            DataColumn2("Name"),
            DataColumn2("Categories"),
            DataColumn2("Quantity", numeric=True),
        ],
        rows=rows,
        heading_row_color=palette.surface_variant,
        bgcolor=palette.surface,
        border=ft.Border.all(1, palette.border),
        border_radius=12,
        vertical_lines=ft.BorderSide(color=palette.border, width=1.5),
        horizontal_lines=ft.BorderSide(color=palette.border, width=1),
        divider_thickness=1,
        heading_text_style=ft.TextStyle(
            color=palette.on_surface,
            weight=ft.FontWeight.BOLD,
        ),
        data_text_style=ft.TextStyle(color=palette.on_surface),
        column_spacing=32,
    )


def _build_search_bar(
    palette: ThemePalette,
    on_change: ft.ControlEventHandler,
) -> ft.SearchBar:
    """Build the catalogue search control."""

    return ft.SearchBar(
        bar_leading=ft.Icon(ft.Icons.SEARCH),
        bar_text_style=ft.TextStyle(
            color=ft.Colors.with_opacity(0.75, palette.on_surface)
        ),
        bar_bgcolor=palette.surface,
        bar_border_side={
            ft.ControlState.DEFAULT: ft.BorderSide(
                color=palette.border,
                width=1.5,
            ),
            ft.ControlState.FOCUSED: ft.BorderSide(
                color=palette.primary,
                width=2,
            ),
        },
        bar_shape=ft.RoundedRectangleBorder(radius=24),
        on_change=on_change,
        expand=True,
    )


def build_catalogue_page(
    palette: ThemePalette,
    storage: StorageHandler | None = None,
    on_food_selected: Callable[[Food], None] | None = None,
    on_add_food: Callable[[], None] | None = None,
) -> ft.Control:
    """Build the searchable food catalogue."""

    data = _load_catalogue_data(storage)
    search_bar: ft.SearchBar
    table_container = ft.Container(expand=True)
    sort_key = "name"

    def refresh_table(
        _: ft.ControlEvent | None = None,
        *,
        update: bool = True,
    ) -> None:
        """Rebuild the table after a search or sort change."""

        query = (search_bar.value or "").strip().casefold()
        foods = _sort_foods(data.foods, data, query, sort_key)
        table_container.content = ft.ListView(
            expand=True,
            spacing=0,
            controls=[
                _build_catalogue_table(
                    _build_catalogue_rows(
                        foods,
                        data,
                        palette,
                        on_food_selected,
                    ),
                    palette,
                )
            ],
        )
        if update:
            table_container.update()

    def search_changed(event: ft.ControlEvent) -> None:
        """Refresh the table when the search query changes."""

        search_bar.value = event.control.value
        refresh_table(event)

    def select_sort(event: ft.ControlEvent) -> None:
        """Apply the sort option selected from the popup menu."""

        nonlocal sort_key
        sort_key = str(event.control.data)
        refresh_table()

    search_bar = _build_search_bar(palette, search_changed)
    sort_menu = ft.PopupMenuButton(
        icon=ft.Icons.SORT,
        icon_color=palette.on_surface,
        tooltip="Sort catalogue",
        items=[
            ft.PopupMenuItem(content="Name", data="name", on_click=select_sort),
            ft.PopupMenuItem(
                content="Categories",
                data="categories",
                on_click=select_sort,
            ),
            ft.PopupMenuItem(
                content="Quantity",
                data="quantity",
                on_click=select_sort,
            ),
        ],
    )

    # Populate the initial table without triggering a page update before the
    # completed layout is returned to Flet.
    refresh_table(update=False)

    return ft.Stack(
        expand=True,
        controls=[
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[search_bar, sort_menu],
                            spacing=8,
                        ),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    ),
                    table_container,
                ],
            ),
            ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    bgcolor=palette.primary,
                    foreground_color=palette.on_surface,
                    tooltip="Add food",
                    on_click=lambda _: on_add_food() if on_add_food else None,
                ),
                alignment=ft.Alignment.BOTTOM_RIGHT,
                padding=ft.Padding.only(right=24, bottom=24),
            ),
        ],
    )


def add_food(
    palette: ThemePalette,
    storage: StorageHandler,
    on_close: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """Build the page used to add a food and its nutrition details."""

    brands = storage.brands.list(limit=FOOD_LIMIT)
    categories = storage.categories.list(limit=CATEGORY_LIMIT)
    units = storage.units.list(limit=UNIT_LIMIT)
    nutrients = storage.nutrients.list(limit=NUTRIENT_LIMIT)

    name_field = ft.TextField(label="Name", autofocus=True)
    brand_field = ft.TextField(label="Brand (optional)")
    category_field = ft.TextField(
        label="Categories (optional)",
        hint_text="Separate multiple categories with commas",
    )
    basis_quantity_field = ft.TextField(
        label="Nutrition basis quantity",
        value="100",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    unit_field = ft.Dropdown(
        label="Nutrition basis unit",
        options=[
            ft.DropdownOption(key=str(unit.id), text=f"{unit.code} ({unit.name})")
            for unit in units
            if unit.id is not None
        ],
        value=(
            str(next((unit.id for unit in units if unit.code == "g"), units[0].id))
            if units
            else None
        ),
    )
    nutrient_fields = {
        nutrient.id: ft.TextField(
            label=f"{nutrient.name} ({nutrient.unit})",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        for nutrient in nutrients
        if nutrient.id is not None
    }
    status = ft.Text(color=palette.error)

    def show_error(message: str) -> None:
        """Display a validation or persistence error on the form."""

        status.value = message
        status.color = palette.error
        status.update()

    def submit(_: ft.ControlEvent) -> None:
        """Validate and persist the food and all entered related details."""

        name = (name_field.value or "").strip()
        if not name:
            show_error("Name is required.")
            return

        try:
            basis_quantity = float((basis_quantity_field.value or "").strip())
        except ValueError:
            show_error("Nutrition basis quantity must be a number.")
            return
        if basis_quantity <= 0:
            show_error("Nutrition basis quantity must be greater than zero.")
            return
        if unit_field.value is None:
            show_error("Select a nutrition basis unit.")
            return

        nutrient_amounts: dict[int, float] = {}
        try:
            for nutrient in nutrients:
                if nutrient.id is None:
                    continue
                amount_text = (nutrient_fields[nutrient.id].value or "").strip()
                if not amount_text:
                    continue
                amount = float(amount_text)
                if amount < 0:
                    raise ValueError("Nutrient amounts cannot be negative.")
                nutrient_amounts[nutrient.id] = amount
        except ValueError as error:
            show_error(str(error))
            return

        try:
            brand_name = (brand_field.value or "").strip()
            brand_id: int | None = None
            if brand_name:
                brand = next(
                    (
                        item
                        for item in brands
                        if item.name.casefold() == brand_name.casefold()
                    ),
                    None,
                )
                if brand is None:
                    brand = storage.brands.create(
                        Brand(id=None, name=brand_name),
                        return_created=True,
                    )
                if brand is None or brand.id is None:
                    raise LookupError("The brand could not be created.")
                brand_id = brand.id

            food = storage.foods.create(
                Food(
                    id=None,
                    name=name,
                    brand_id=brand_id,
                    created_at=datetime.now(),
                ),
                return_created=True,
            )
            if food is None or food.id is None:
                raise LookupError("The food could not be created.")

            category_names = {
                category_name.strip()
                for category_name in (category_field.value or "").split(",")
                if category_name.strip()
            }
            known_categories = {
                category.name.casefold(): category for category in categories
            }
            for category_name in category_names:
                category = known_categories.get(category_name.casefold())
                if category is None:
                    category = storage.categories.create(
                        Category(id=None, name=category_name),
                        return_created=True,
                    )
                if category is None or category.id is None:
                    raise LookupError("A category could not be created.")
                storage.food_categories.create(
                    FoodCategory(food_id=food.id, category_id=category.id)
                )

            base = storage.food_nutrient_bases.create(
                FoodNutrientBase(
                    id=None,
                    food_id=food.id,
                    basis_unit_id=int(unit_field.value),
                    basis_quantity=basis_quantity,
                ),
                return_created=True,
            )
            if base is None or base.id is None:
                raise LookupError("The nutrition basis could not be created.")

            for nutrient_id, amount in nutrient_amounts.items():
                storage.food_nutrients.create(
                    FoodNutrient(
                        food_id=food.id,
                        base_id=base.id,
                        nutrient_type_id=nutrient_id,
                        amount=amount,
                    )
                )
        except ValueError as error:
            show_error(str(error))
            return
        except LookupError as error:
            show_error(str(error))
            return
        except sqlite3.IntegrityError:
            show_error("A food with this name and brand already exists.")
            return

        on_close(_)

    form_controls: list[ft.Control] = [
        ft.Text("Add food", size=28, weight=ft.FontWeight.BOLD),
        name_field,
        brand_field,
        category_field,
        ft.Row(controls=[basis_quantity_field, unit_field], spacing=12),
    ]
    if nutrient_fields:
        form_controls.extend(
            [
                ft.Text("Nutrients", size=20, weight=ft.FontWeight.BOLD),
                *nutrient_fields.values(),
            ]
        )
    form_controls.extend(
        [
            status,
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.TextButton("Cancel", on_click=on_close),
                    ft.FilledButton("Submit", on_click=submit),
                ],
            ),
        ]
    )

    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=palette.on_surface,
                        tooltip="Close add food",
                        on_click=on_close,
                    )
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=form_controls,
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=24,
                expand=True,
            ),
        ],
    )
