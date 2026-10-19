from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


def _row_to_mapping(row: object) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    return dict(row)


@dataclass(frozen=True, slots=True)
class MealEntry:
    id: int | None
    occurred_on: date
    meal: str
    calories_kcal: int
    spend_usd: float
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    notes: str = ""
    created_at: datetime | None = None

    @classmethod
    def from_row(cls, row: object) -> MealEntry:
        row_mapping = _row_to_mapping(row)
        created_at_value = row_mapping["created_at"]
        return cls(
            id=row_mapping["id"],
            occurred_on=date.fromisoformat(row_mapping["occurred_on"]),
            meal=row_mapping["meal"],
            calories_kcal=int(row_mapping["calories_kcal"]),
            spend_usd=float(row_mapping["spend_usd"]),
            protein_g=float(row_mapping.get("protein_g", 0.0)),
            carbs_g=float(row_mapping.get("carbs_g", 0.0)),
            fat_g=float(row_mapping.get("fat_g", 0.0)),
            notes=row_mapping.get("notes") or "",
            created_at=datetime.fromisoformat(created_at_value) if created_at_value else None,
        )

    def to_record(self) -> dict[str, object]:
        return {
            "occurred_on": self.occurred_on.isoformat(),
            "meal": self.meal,
            "calories_kcal": self.calories_kcal,
            "spend_usd": self.spend_usd,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "notes": self.notes,
            "created_at": (self.created_at or datetime.now()).isoformat(timespec="seconds"),
        }


@dataclass(frozen=True, slots=True)
class GroceryShoppingEntry:
    id: int | None
    occurred_on: date
    items: list[MealEntry]
    spend_usd: float
    notes: str = ""

    @classmethod
    def from_row(cls, row: object) -> GroceryShoppingEntry:
        row_mapping = _row_to_mapping(row)
        items_value = row_mapping.get("items", [])
        if isinstance(items_value, list):
            items = [item if isinstance(item, MealEntry) else MealEntry.from_row(item) for item in items_value]
        else:
            items = []

        occurred_on_value = row_mapping.get("occurred_on")
        if isinstance(occurred_on_value, date):
            occurred_on = occurred_on_value
        elif occurred_on_value:
            occurred_on = date.fromisoformat(str(occurred_on_value))
        else:
            occurred_on = date.today()

        return cls(
            id=row_mapping.get("id"),
            occurred_on=occurred_on,
            items=items,
            spend_usd=float(row_mapping.get("spend_usd", 0.0)),
            notes=row_mapping.get("notes") or "",
        )

    def to_record(self) -> dict[str, object]:
        return {
            "occurred_on": self.occurred_on.isoformat(),
            "items": [item.to_record() for item in self.items],
            "spend_usd": self.spend_usd,
            "notes": self.notes,
        }
