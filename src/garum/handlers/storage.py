"""SQLite database access and typed repositories."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import fields
from pathlib import Path
from typing import Any, Generic, Iterable, Iterator, TypeVar

from .models import (
    Brand,
    Category,
    Consumption,
    Food,
    FoodCategory,
    FoodEntry,
    GroceryBill,
    Inventory,
    NutritionRecommendationSource,
    Nutrient,
    NutrientProfile,
    NutrientValue,
    PriceHistory,
    Purchase,
    Recipe,
    RecipeIngredient,
    Store,
    StoreItem,
    SuggestedFrequency,
    Unit,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "data" / "db.sql"

T = TypeVar("T")


class SQLiteDatabase:
    """Connection and transaction boundary for one SQLite database."""

    def __init__(self, database_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
        self.database_path = Path(database_path)
        self.schema_path = Path(schema_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self) -> None:
        if not self.schema_path.is_file():
            raise FileNotFoundError(f"Database schema not found: {self.schema_path}")
        with self.connection() as connection:
            connection.executescript(self.schema_path.read_text(encoding="utf-8"))

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
        except BaseException:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()


class RowRepository(Generic[T]):
    """CRUD operations for one typed SQLite table."""

    def __init__(self, database: SQLiteDatabase, model_type: type[T], table: str) -> None:
        self.database = database
        self.model_type = model_type
        self.table = table
        self._model_columns = tuple(field.name for field in fields(model_type))

    def list(self, *, limit: int = 100, order_by: str | None = None) -> list[T]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        sort_column = order_by or ("id" if "id" in self._model_columns else self._model_columns[0])
        if sort_column not in self._model_columns:
            raise ValueError(f"invalid order column: {sort_column}")
        with self.database.connection() as connection:
            rows = connection.execute(
                f"SELECT {', '.join(self._model_columns)} FROM {self.table} "
                f"ORDER BY {sort_column} LIMIT ?",
                (limit,),
            ).fetchall()
        return [self.model_type.from_row(row) for row in rows]  # type: ignore[attr-defined]

    def get(self, row_id: int) -> T | None:
        if "id" not in self._model_columns:
            raise TypeError(f"{self.table} does not have a single id column")
        with self.database.connection() as connection:
            row = connection.execute(
                f"SELECT {', '.join(self._model_columns)} FROM {self.table} WHERE id = ?",
                (row_id,),
            ).fetchone()
        return self.model_type.from_row(row) if row is not None else None  # type: ignore[attr-defined]

    def create(self, model: T) -> T:
        record = model.to_record()  # type: ignore[attr-defined]
        record = {key: value for key, value in record.items() if value is not None}
        columns = ", ".join(record)
        placeholders = ", ".join(f":{column}" for column in record)
        with self.database.connection() as connection:
            cursor = connection.execute(
                f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})",
                record,
            )
            if "id" in self._model_columns:
                row = connection.execute(
                    f"SELECT {', '.join(self._model_columns)} FROM {self.table} WHERE id = ?",
                    (cursor.lastrowid,),
                ).fetchone()
            else:
                row = connection.execute(
                    f"SELECT {', '.join(self._model_columns)} FROM {self.table} WHERE "
                    + " AND ".join(f"{column} = :{column}" for column in record),
                    record,
                ).fetchone()
        return self.model_type.from_row(row)  # type: ignore[attr-defined]

    def update(self, model: T) -> T:
        record = model.to_record()  # type: ignore[attr-defined]
        row_id = getattr(model, "id", None)
        if row_id is None:
            raise ValueError("update requires a model with an id")
        record = {key: value for key, value in record.items() if key != "id"}
        assignments = ", ".join(f"{column} = :{column}" for column in record)
        record["id"] = row_id
        with self.database.connection() as connection:
            connection.execute(f"UPDATE {self.table} SET {assignments} WHERE id = :id", record)
            row = connection.execute(
                f"SELECT {', '.join(self._model_columns)} FROM {self.table} WHERE id = :id",
                record,
            ).fetchone()
        if row is None:
            raise LookupError(f"{self.table} row {row_id} does not exist")
        return self.model_type.from_row(row)  # type: ignore[attr-defined]

    def delete(self, row_id: int) -> bool:
        with self.database.connection() as connection:
            cursor = connection.execute(f"DELETE FROM {self.table} WHERE id = ?", (row_id,))
        return cursor.rowcount > 0

    def delete_where(self, **filters: object) -> bool:
        if not filters or any(column not in self._model_columns for column in filters):
            raise ValueError("delete_where requires valid model columns")
        clauses = " AND ".join(f"{column} = :{column}" for column in filters)
        with self.database.connection() as connection:
            cursor = connection.execute(f"DELETE FROM {self.table} WHERE {clauses}", filters)
        return cursor.rowcount > 0


class FoodEntryRepository(RowRepository[FoodEntry]):
    """Repository for historical food diary rows."""

    def __init__(self, database_path: Path, *, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
        database = SQLiteDatabase(database_path, schema_path)
        super().__init__(database, FoodEntry, "food_entries")

    def list_food_entries(self, *, limit: int = 100) -> list[FoodEntry]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        columns = ", ".join(self._model_columns)
        with self.database.connection() as connection:
            rows = connection.execute(
                f"SELECT {columns} FROM food_entries "
                "ORDER BY occurred_on DESC, created_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [FoodEntry.from_row(row) for row in rows]

    def count_food_entries(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM food_entries").fetchone()
        return int(row["count"])

    def create_food_entry(self, entry: FoodEntry) -> FoodEntry:
        return self.create(entry)

    def delete_food_entry(self, entry_id: int) -> bool:
        return self.delete(entry_id)

    def seed_if_empty(self, entries: Iterable[FoodEntry]) -> None:
        if self.count_food_entries() > 0:
            return
        for entry in entries:
            self.create(entry)


class GarumStorage:
    """Typed repositories for all rows in the Garum schema."""

    def __init__(self, database_path: Path, *, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
        database = SQLiteDatabase(database_path, schema_path)
        self.brands = RowRepository(database, Brand, "brands")
        self.categories = RowRepository(database, Category, "categories")
        self.units = RowRepository(database, Unit, "units")
        self.sources = RowRepository(database, NutritionRecommendationSource, "nutrition_recommendation_sources")
        self.foods = RowRepository(database, Food, "foods")
        self.food_categories = RowRepository(database, FoodCategory, "food_categories")
        self.nutrient_profiles = RowRepository(database, NutrientProfile, "nutrient_profiles")
        self.nutrients = RowRepository(database, Nutrient, "nutrients")
        self.nutrient_values = RowRepository(database, NutrientValue, "nutrient_values")
        self.consumptions = RowRepository(database, Consumption, "consumptions")
        self.suggested_frequencies = RowRepository(database, SuggestedFrequency, "suggested_frequencies")
        self.recipes = RowRepository(database, Recipe, "recipes")
        self.recipe_ingredients = RowRepository(database, RecipeIngredient, "recipe_ingredients")
        self.inventory = RowRepository(database, Inventory, "inventory")
        self.food_entries = RowRepository(database, FoodEntry, "food_entries")
        self.stores = RowRepository(database, Store, "stores")
        self.store_items = RowRepository(database, StoreItem, "store_items")
        self.price_history = RowRepository(database, PriceHistory, "price_history")
        self.grocery_bills = RowRepository(database, GroceryBill, "grocery_bills")
        self.purchases = RowRepository(database, Purchase, "purchases")
