"""
SQLite database access and repositories.

This module performs connections, transactions, schema setup, and SQL.
It returns models from models.py but contains no domain representation logic.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from .models import FoodEntry

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "data" / "db.sql"

_FOOD_ENTRY_COLUMNS = (
    "id, occurred_on, meal, food_id, recipe_id, quantity, unit_id, "
    "calories_kcal, spend_usd, protein_g, carbs_g, fat_g, sugar_g, "
    "saturated_fat_g, fiber_g, sodium_mg, calcium_mg, iron_mg, magnesium_mg, "
    "potassium_mg, vitamin_a_ug, vitamin_c_mg, vitamin_d_ug, vitamin_b12_ug, "
    "folate_ug, notes, created_at"
)
_FOOD_ENTRY_RECORD_COLUMNS = ", ".join(_FOOD_ENTRY_COLUMNS.split(", ")[1:])


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


class FoodEntryRepository:
    """Repository for ``food_entries`` rows."""

    def __init__(
        self,
        database_path: Path,
        *,
        schema_path: Path = DEFAULT_SCHEMA_PATH,
    ) -> None:
        self.database = SQLiteDatabase(database_path, schema_path)

    def list_food_entries(self, *, limit: int = 100) -> list[FoodEntry]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        with self.database.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT {_FOOD_ENTRY_COLUMNS}
                FROM food_entries
                ORDER BY occurred_on DESC, created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [FoodEntry.from_row(row) for row in rows]

    def count_food_entries(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM food_entries").fetchone()
        return int(row["count"])

    def create_food_entry(self, entry: FoodEntry) -> FoodEntry:
        record = entry.to_record()
        columns = _FOOD_ENTRY_RECORD_COLUMNS
        placeholders = ", ".join(f":{column}" for column in columns.split(", "))
        with self.database.connection() as connection:
            cursor = connection.execute(
                f"INSERT INTO food_entries ({columns}) VALUES ({placeholders})",
                record,
            )
            row = connection.execute(
                f"SELECT {_FOOD_ENTRY_COLUMNS} FROM food_entries WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return FoodEntry.from_row(row)

    def delete_food_entry(self, entry_id: int) -> bool:
        with self.database.connection() as connection:
            cursor = connection.execute("DELETE FROM food_entries WHERE id = ?", (entry_id,))
        return cursor.rowcount > 0

    def seed_if_empty(self, entries: Iterable[FoodEntry]) -> None:
        if self.count_food_entries() > 0:
            return
        records = [entry.to_record() for entry in entries]
        if not records:
            return
        columns = _FOOD_ENTRY_RECORD_COLUMNS
        placeholders = ", ".join(f":{column}" for column in columns.split(", "))
        with self.database.connection() as connection:
            connection.executemany(
                f"INSERT INTO food_entries ({columns}) VALUES ({placeholders})",
                records,
            )
