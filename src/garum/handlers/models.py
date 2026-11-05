"""
Typed database row models.
The models describe rows and serialization only with no database access.
"""

# First-party imports
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, ClassVar, Mapping


# Helper function to convert a row to a mapping, handling both Mapping and other types (like tuples).
def _row_mapping(row: Mapping[str, Any] | Any) -> Mapping[str, Any]:
    return row if isinstance(row, Mapping) else dict(row)


# Helper function to get a value from a row mapping with an optional default.
def _value(row: Mapping[str, Any], key: str, default: Any = None) -> Any:
    value = row.get(key, default)
    return default if value is None and default is not None else value


# Convert a value to a datetime object, accepting either a datetime or an ISO 8601 string.
def _as_datetime(value: datetime | str | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


# Convert a value to a date object, accepting either a date or an ISO 8601 string.
def _as_date(value: date | str) -> date:
    return value if isinstance(value, date) else date.fromisoformat(value)


# Convert a dataclass instance to a dictionary suitable for database insertion or update.
def _record(instance: Any) -> dict[str, object]:
    values = asdict(instance)
    values.pop("id", None)
    for key, value in values.items():
        if isinstance(value, (date, datetime)):
            values[key] = value.isoformat()
    return values


# --- dataclass definitions for various database row models follow, each with methods to convert from a database row and to a record dictionary.
#     frozen=True makes the instances immutable, and slots=True optimizes memory usage by preventing the creation of a __dict__ for each instance.
#     @classmethod makes from_row a class method rather than an instance method, making it possible to create an instance of the class from a database
#     row without needing an existing instance.


@dataclass(frozen=True, slots=True)
class Brand:
    id: int | None
    name: str

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Brand:
        values = _row_mapping(row)
        return cls(values.get("id"), values["name"])

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Category:
    id: int | None
    name: str

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Category:
        values = _row_mapping(row)
        return cls(values.get("id"), values["name"])

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Unit:
    id: int | None
    code: str
    name: str
    kind: str

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Unit:
        values = _row_mapping(row)
        return cls(values.get("id"), values["code"], values["name"], values["kind"])

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class NutritionRecommendationSource:
    id: int | None
    name: str
    version: str | None = None
    url: str | None = None
    retrieved_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> NutritionRecommendationSource:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["name"],
            values.get("version"),
            values.get("url"),
            _as_datetime(values.get("retrieved_at")),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Food:
    id: int | None
    name: str
    brand_id: int | None = None
    is_food: bool = True
    created_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Food:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["name"],
            values.get("brand_id"),
            bool(values.get("is_food", 1)),
            _as_datetime(values.get("created_at")),
        )

    def to_record(self) -> dict[str, object]:
        record = _record(self)
        record["is_food"] = int(self.is_food)
        return record


@dataclass(frozen=True, slots=True)
class FoodCategory:
    food_id: int
    category_id: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> FoodCategory:
        values = _row_mapping(row)
        return cls(values["food_id"], values["category_id"])

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class NutrientProfile:
    id: int | None
    food_id: int
    basis_unit_id: int
    basis_quantity: float = 100.0
    serving_name: str | None = None
    serving_quantity: float | None = None
    serving_unit_id: int | None = None
    source_id: int | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> NutrientProfile:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["food_id"],
            values["basis_unit_id"],
            float(values["basis_quantity"]),
            values.get("serving_name"),
            values.get("serving_quantity"),
            values.get("serving_unit_id"),
            values.get("source_id"),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Nutrient:
    id: int | None
    type: str
    code: str
    name: str
    unit: str

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Nutrient:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["type"],
            values["code"],
            values["name"],
            values["unit"],
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class NutrientValue:
    profile_id: int
    nutrient_type_id: int
    amount: float

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> NutrientValue:
        values = _row_mapping(row)
        return cls(
            values["profile_id"], values["nutrient_type_id"], float(values["amount"])
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Consumption:
    id: int | None
    food_id: int
    name: str
    quantity: float
    unit_id: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Consumption:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["food_id"],
            values["name"],
            float(values["quantity"]),
            values["unit_id"],
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class SuggestedFrequency:
    id: int | None
    category_id: int
    frequency_per_week: float
    amount: float
    unit_id: int
    source_id: int | None = None
    valid_from: date | None = None
    valid_to: date | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> SuggestedFrequency:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["category_id"],
            float(values["frequency_per_week"]),
            float(values["amount"]),
            values["unit_id"],
            values.get("source_id"),
            _as_date(values["valid_from"]) if values.get("valid_from") else None,
            _as_date(values["valid_to"]) if values.get("valid_to") else None,
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Recipe:
    id: int | None
    name: str
    servings: int = 1
    calories_kcal: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    sugar_g: float = 0.0
    fat_g: float = 0.0
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
    created_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Recipe:
        values = _row_mapping(row)
        fields = {
            field: _value(values, field, 0.0)
            for field in cls.__dataclass_fields__
            if field not in {"id", "name", "created_at"}
        }
        fields["servings"] = int(fields["servings"])
        fields["created_at"] = _as_datetime(values.get("created_at"))
        return cls(values.get("id"), values["name"], **fields)

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    recipe_id: int
    food_id: int
    quantity: float
    unit_id: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> RecipeIngredient:
        values = _row_mapping(row)
        return cls(
            values["recipe_id"],
            values["food_id"],
            float(values["quantity"]),
            values["unit_id"],
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Inventory:
    id: int | None
    quantity: float
    unit_id: int
    food_id: int | None = None
    description: str = ""
    updated_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Inventory:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            float(values["quantity"]),
            values["unit_id"],
            values.get("food_id"),
            values.get("description", ""),
            _as_datetime(values.get("updated_at")),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class FoodEntry:
    """A snapshot of one consumed food event stored in food_entries."""

    id: int | None
    occurred_on: date
    meal: str
    calories_kcal: float
    spend_usd: float
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

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> FoodEntry:
        values = _row_mapping(row)
        fields = {
            field: float(_value(values, field, 0.0))
            for field in (
                "protein_g",
                "carbs_g",
                "fat_g",
                "sugar_g",
                "saturated_fat_g",
                "fiber_g",
                "sodium_mg",
                "calcium_mg",
                "iron_mg",
                "magnesium_mg",
                "potassium_mg",
                "vitamin_a_ug",
                "vitamin_c_mg",
                "vitamin_d_ug",
                "vitamin_b12_ug",
                "folate_ug",
            )
        }
        return cls(
            values.get("id"),
            _as_date(values["occurred_on"]),
            values["meal"],
            float(values["calories_kcal"]),
            float(values["spend_usd"]),
            food_id=values.get("food_id"),
            recipe_id=values.get("recipe_id"),
            quantity=values.get("quantity"),
            unit_id=values.get("unit_id"),
            notes=_value(values, "notes", "") or "",
            created_at=_as_datetime(values.get("created_at")),
            **fields,
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Store:
    id: int | None
    name: str
    location: str | None = None
    maps_link: str | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Store:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["name"],
            values.get("location"),
            values.get("maps_link"),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class StoreItem:
    store_id: int
    food_id: int
    current_price: float = 0.0
    package_quantity: float | None = None
    package_unit_id: int | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> StoreItem:
        values = _row_mapping(row)
        return cls(
            values["store_id"],
            values["food_id"],
            float(values["current_price"]),
            values.get("package_quantity"),
            values.get("package_unit_id"),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class PriceHistory:
    id: int | None
    store_id: int
    food_id: int
    price: float
    observed_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> PriceHistory:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["store_id"],
            values["food_id"],
            float(values["price"]),
            _as_datetime(values.get("observed_at")),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class GroceryBill:
    id: int | None
    store_id: int
    total_amount: float
    purchased_at: datetime | None = None
    notes: str = ""

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> GroceryBill:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["store_id"],
            float(values["total_amount"]),
            _as_datetime(values.get("purchased_at")),
            values.get("notes", ""),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)


@dataclass(frozen=True, slots=True)
class Purchase:
    id: int | None
    store_id: int
    food_id: int
    quantity: float
    unit_id: int
    unit_price: float
    discount_percent: float = 0.0
    bill_id: int | None = None
    purchased_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any] | Any) -> Purchase:
        values = _row_mapping(row)
        return cls(
            values.get("id"),
            values["store_id"],
            values["food_id"],
            float(values["quantity"]),
            values["unit_id"],
            float(values["unit_price"]),
            float(values.get("discount_percent", 0)),
            values.get("bill_id"),
            _as_datetime(values.get("purchased_at")),
        )

    def to_record(self) -> dict[str, object]:
        return _record(self)
