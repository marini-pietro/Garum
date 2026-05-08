from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .models import MealEntry


class MealEntryStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS food_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_on TEXT NOT NULL,
                    meal TEXT NOT NULL,
                    calories_kcal INTEGER NOT NULL,
                    spend_usd REAL NOT NULL,
                    protein_g REAL NOT NULL DEFAULT 0,
                    carbs_g REAL NOT NULL DEFAULT 0,
                    fat_g REAL NOT NULL DEFAULT 0,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )

    def list_entries(self, *, limit: int = 100) -> list[MealEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    occurred_on,
                    meal,
                    calories_kcal,
                    spend_usd,
                    protein_g,
                    carbs_g,
                    fat_g,
                    notes,
                    created_at
                FROM food_entries
                ORDER BY occurred_on DESC, created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [MealEntry.from_row(row) for row in rows]

    def count_entries(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM food_entries").fetchone()
        return int(row["count"])

    def add_entry(self, entry: MealEntry) -> MealEntry:
        record = entry.to_record()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO food_entries (
                    occurred_on,
                    meal,
                    calories_kcal,
                    spend_usd,
                    protein_g,
                    carbs_g,
                    fat_g,
                    notes,
                    created_at
                )
                VALUES (:occurred_on, :meal, :calories_kcal, :spend_usd, :protein_g, :carbs_g, :fat_g, :notes, :created_at)
                """,
                record,
            )
            inserted_id = cursor.lastrowid

        return MealEntry(
            id=int(inserted_id),
            occurred_on=entry.occurred_on,
            meal=entry.meal,
            calories_kcal=entry.calories_kcal,
            spend_usd=entry.spend_usd,
            protein_g=entry.protein_g,
            carbs_g=entry.carbs_g,
            fat_g=entry.fat_g,
            notes=entry.notes,
            created_at=entry.created_at,
        )

    def delete_entry(self, entry_id: int) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM food_entries WHERE id = ?", (entry_id,))

    def seed_if_empty(self, entries: Iterable[MealEntry]) -> None:
        if self.count_entries() > 0:
            return

        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO food_entries (
                    occurred_on,
                    meal,
                    calories_kcal,
                    spend_usd,
                    protein_g,
                    carbs_g,
                    fat_g,
                    notes,
                    created_at
                )
                VALUES (:occurred_on, :meal, :calories_kcal, :spend_usd, :protein_g, :carbs_g, :fat_g, :notes, :created_at)
                """,
                [entry.to_record() for entry in entries],
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection
