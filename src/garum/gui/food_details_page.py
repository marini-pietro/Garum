"""
Page showing a food's nutritional information.
"""


def _load_food_detail_data(
    storage: StorageHandler,
    food: Food,
) -> tuple[list[str], str, list[DataRow2]]:
    """Load category and nutrient data needed by the food detail page."""

    categories = {
        category.id: category.name
        for category in storage.categories.list(limit=CATEGORY_LIMIT)
    }
    food_categories = [
        categories[link.category_id]
        for link in storage.food_categories.list(limit=FOOD_CATEGORY_LIMIT)
        if link.food_id == food.id and link.category_id in categories
    ]

    nutrients = {
        nutrient.id: nutrient
        for nutrient in storage.nutrients.list(limit=NUTRIENT_LIMIT)
    }
    units = {unit.id: unit.code for unit in storage.units.list(limit=UNIT_LIMIT)}
    bases = [
        base
        for base in storage.food_nutrient_bases.list(limit=FOOD_BASE_LIMIT)
        if base.food_id == food.id
    ]
    base = bases[0] if bases else None

    nutrient_rows = []
    for item in storage.food_nutrients.list(limit=FOOD_NUTRIENT_LIMIT):
        if base is None or item.food_id != food.id or item.base_id != base.id:
            continue
        nutrient = nutrients.get(item.nutrient_type_id)
        if nutrient is None:
            continue
        nutrient_rows.append(
            DataRow2(
                cells=[
                    ft.DataCell(ft.Text(nutrient.name)),
                    ft.DataCell(ft.Text(f"{item.amount:g} {nutrient.unit}")),
                ]
            )
        )

    basis = (
        f"Per {base.basis_quantity:g} {units.get(base.basis_unit_id, '')}".strip()
        if base is not None
        else "No nutrition basis available"
    )
    return food_categories, basis, nutrient_rows


def _build_food_detail_table(
    rows: list[DataRow2],
    palette: ThemePalette,
) -> DataTable2:
    """Build the nutrient table used on the food detail page."""

    return DataTable2(
        columns=[
            DataColumn2("Nutrient"),
            DataColumn2("Amount", numeric=True),
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
    )


def build_food_detail_page(
    palette: ThemePalette,
    storage: StorageHandler,
    food: Food,
    on_close: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """Build a page showing a food's nutritional information."""

    food_categories, basis, nutrient_rows = _load_food_detail_data(storage, food)

    return ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=palette.on_surface,
                            tooltip="Close food details",
                            on_click=on_close,
                        )
                    ],
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            food.name,
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            ", ".join(sorted(food_categories)) or "No categories",
                            color=palette.muted,
                        ),
                        ft.Text(basis, color=palette.muted),
                        _build_food_detail_table(nutrient_rows, palette),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                ),
                padding=24,
                expand=True,
            ),
        ],
    )
