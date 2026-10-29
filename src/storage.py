from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

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
            schema_path = Path(__file__).resolve().parent.parent / "data" / "db.sql"
            if not schema_path.is_file():
                raise FileNotFoundError(f"Database schema not found: {schema_path}")
            connection.executescript(schema_path.read_text(encoding="utf-8"))

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
                    sugar_g,
                    saturated_fat_g,
                    fiber_g,
                    sodium_mg,
                    calcium_mg,
                    iron_mg,
                    magnesium_mg,
                    potassium_mg,
                    vitamin_a_ug,
                    vitamin_c_mg,
                    vitamin_d_ug,
                    vitamin_b12_ug,
                    folate_ug,
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
                    sugar_g,
                    saturated_fat_g,
                    fiber_g,
                    sodium_mg,
                    calcium_mg,
                    iron_mg,
                    magnesium_mg,
                    potassium_mg,
                    vitamin_a_ug,
                    vitamin_c_mg,
                    vitamin_d_ug,
                    vitamin_b12_ug,
                    folate_ug,
                    notes,
                    created_at
                )
                VALUES (
                    :occurred_on, :meal, :calories_kcal, :spend_usd,
                    :protein_g, :carbs_g, :fat_g, :sugar_g,
                    :saturated_fat_g, :fiber_g, :sodium_mg, :calcium_mg,
                    :iron_mg, :magnesium_mg, :potassium_mg, :vitamin_a_ug,
                    :vitamin_c_mg, :vitamin_d_ug, :vitamin_b12_ug, :folate_ug,
                    :notes, :created_at
                )
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
            sugar_g=entry.sugar_g,
            saturated_fat_g=entry.saturated_fat_g,
            fiber_g=entry.fiber_g,
            sodium_mg=entry.sodium_mg,
            calcium_mg=entry.calcium_mg,
            iron_mg=entry.iron_mg,
            magnesium_mg=entry.magnesium_mg,
            potassium_mg=entry.potassium_mg,
            vitamin_a_ug=entry.vitamin_a_ug,
            vitamin_c_mg=entry.vitamin_c_mg,
            vitamin_d_ug=entry.vitamin_d_ug,
            vitamin_b12_ug=entry.vitamin_b12_ug,
            folate_ug=entry.folate_ug,
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
                    sugar_g,
                    saturated_fat_g,
                    fiber_g,
                    sodium_mg,
                    calcium_mg,
                    iron_mg,
                    magnesium_mg,
                    potassium_mg,
                    vitamin_a_ug,
                    vitamin_c_mg,
                    vitamin_d_ug,
                    vitamin_b12_ug,
                    folate_ug,
                    notes,
                    created_at
                )
                VALUES (
                    :occurred_on, :meal, :calories_kcal, :spend_usd,
                    :protein_g, :carbs_g, :fat_g, :sugar_g,
                    :saturated_fat_g, :fiber_g, :sodium_mg, :calcium_mg,
                    :iron_mg, :magnesium_mg, :potassium_mg, :vitamin_a_ug,
                    :vitamin_c_mg, :vitamin_d_ug, :vitamin_b12_ug, :folate_ug,
                    :notes, :created_at
                )
                """,
                [entry.to_record() for entry in entries],
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        except BaseException:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()
