"""Database row models used by the application.

Models describe the shape and conversion of data.
This module does not open database connections or execute SQL.
Persistence is handled by storage.py.
"""

# First-party imports
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Mapping

# Define value validation helper function (returns default if value is None)
def _value(row: Mapping[str, Any], key: str, default: Any = None) -> Any:
    value = row.get(key, default)
    return default if value is None and default is not None else value

# Define date conversion helper function
def _as_date(value: date | str) -> date:
    return value if isinstance(value, date) else date.fromisoformat(value)

# Define datetime conversion helper function
def _as_datetime(value: datetime | str | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

# Define row mapping helper function (converts a database row to a dictionary)
def _row_mapping(row: Mapping[str, Any] | Any) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return row
    return dict(row)

# Define FoodEntry as an immutable (because of frozen=true) dataclass; slots reduce per-instance memory usage.
@dataclass(frozen=True, slots=True)
class FoodEntry:
    """A snapshot of one consumed food event stored in ``food_entries``."""

    id: int | None
    occurred_on: date
    meal: str
    calories_kcal: float
    spend_usd: float
    notes: str = ""
    created_at: datetime | None = None
    food_id: int | None = None
    recipe_id: int | None = None
    quantity: float | None = None
    unit_id: int | None = None
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    sugar_g: float = 0.0
    saturated_fat_g: float = 0.0
    fiber_g: float = 0.0
    sodium_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    magnesium_mg: float = 0.0
    potassium_mg: float = 0.0
    vitamin_a_ug: float = 0.0
    vitamin_c_mg: float = 0.0
    vitamin_d_ug: float = 0.0
    vitamin_b12_ug: float = 0.0
    folate_ug: float = 0.0
    notes: str = ""
    created_at: datetime | None = None
    food_id: int | None = None
    recipe_id: int | None = None
    quantity: float | None = None
    unit_id: int | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> FoodEntry:
        values = _row_mapping(row)
        return cls(
            id=values.get("id"),
            occurred_on=_as_date(values["occurred_on"]),
            meal=values["meal"],
            calories_kcal=float(values["calories_kcal"]),
            spend_usd=float(values["spend_usd"]),
            protein_g=float(_value(values, "protein_g", 0.0)),
            carbs_g=float(_value(values, "carbs_g", 0.0)),
            fat_g=float(_value(values, "fat_g", 0.0)),
            sugar_g=float(_value(values, "sugar_g", 0.0)),
            saturated_fat_g=float(_value(values, "saturated_fat_g", 0.0)),
            fiber_g=float(_value(values, "fiber_g", 0.0)),
            sodium_mg=float(_value(values, "sodium_mg", 0.0)),
            calcium_mg=float(_value(values, "calcium_mg", 0.0)),
            iron_mg=float(_value(values, "iron_mg", 0.0)),
            magnesium_mg=float(_value(values, "magnesium_mg", 0.0)),
            potassium_mg=float(_value(values, "potassium_mg", 0.0)),
            vitamin_a_ug=float(_value(values, "vitamin_a_ug", 0.0)),
            vitamin_c_mg=float(_value(values, "vitamin_c_mg", 0.0)),
            vitamin_d_ug=float(_value(values, "vitamin_d_ug", 0.0)),
            vitamin_b12_ug=float(_value(values, "vitamin_b12_ug", 0.0)),
            folate_ug=float(_value(values, "folate_ug", 0.0)),
            notes=_value(values, "notes", "") or "",
            created_at=_as_datetime(values.get("created_at")),
            food_id=values.get("food_id"),
            recipe_id=values.get("recipe_id"),
            quantity=values.get("quantity"),
            unit_id=values.get("unit_id"),
        )

    def to_record(self) -> dict[str, object]:
        """Return a dictionary suitable for an INSERT or UPDATE query."""
        return {
            "occurred_on": self.occurred_on.isoformat(),
            "meal": self.meal,
            "food_id": self.food_id,
            "recipe_id": self.recipe_id,
            "quantity": self.quantity,
            "unit_id": self.unit_id,
            "calories_kcal": self.calories_kcal,
            "spend_usd": self.spend_usd,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "sugar_g": self.sugar_g,
            "saturated_fat_g": self.saturated_fat_g,
            "fiber_g": self.fiber_g,
            "sodium_mg": self.sodium_mg,
            "calcium_mg": self.calcium_mg,
            "iron_mg": self.iron_mg,
            "magnesium_mg": self.magnesium_mg,
            "potassium_mg": self.potassium_mg,
            "vitamin_a_ug": self.vitamin_a_ug,
            "vitamin_c_mg": self.vitamin_c_mg,
            "vitamin_d_ug": self.vitamin_d_ug,
            "vitamin_b12_ug": self.vitamin_b12_ug,
            "folate_ug": self.folate_ug,
            "notes": self.notes,
            "created_at": (self.created_at or datetime.now()).isoformat(timespec="seconds"),
        }
