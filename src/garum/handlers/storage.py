"""
SQLite database access and typed repositories.
"""

# First-party imports
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import fields
from pathlib import Path
from typing import Any, Generic, Iterable, Iterator, TypeVar

# Third-party imports
import sqlite3

# Local imports
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

# Define project root and default schema path for the SQLite database.
# The project root is determined by resolving the current file's path and navigating up three parent directories.
# The default schema path points to a SQL file that contains the database schema.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA_PATH: Path = PROJECT_ROOT / "data" / "db.sql"


class SQLiteDatabase:
    """
    Connection and transaction boundary for one SQLite database.
    """

    def __init__(
        self, database_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH
    ) -> None:
        """
        Initialize the SQLiteDatabase instance with the provided database and schema paths.
        """

        # Store the database and schema paths as Path objects for later use.
        self.database_path = Path(database_path)
        self.schema_path = Path(schema_path)

        # Ensure that the parent directory of the database path exists, creating it if necessary.
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the SQLite database by creating the database file if it doesn't exist and applying the schema.
        self.initialize()

    def initialize(self) -> None:
        """
        Initialize the SQLite database by creating the database file if it doesn't exist and applying the schema.
        Separate from __init__ to allow for re-initialization and to allows for easier testing and mocking of the database connection.
        Does not reset the database nor delete data on re-initialization (unless the script itself does so, e.g. with DROP TABLE).
        Re-initialization is only safe when the database is idempotent, i.e. the schema script does not modify existing tables or data
        (e.g. because it uses CREATE TABLE IF NOT EXISTS).
        """

        if not self.schema_path.is_file():
            raise FileNotFoundError(f"Database schema not found: {self.schema_path}")
        with self.connection() as connection:
            connection.executescript(self.schema_path.read_text(encoding="utf-8"))

    # contextmanager decorator allows this method to be used in a with statement,
    # ensuring that the connection is properly closed after use.
    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """
        Context manager for a SQLite database connection.
        This method yields a SQLite connection object that can be used to execute SQL queries.
        """

        # Create a new SQLite connection to the database file specified by self.database_path.
        connection = sqlite3.connect(self.database_path)

        # Set the row factory to sqlite3.Row, which allows accessing columns by column name.
        connection.row_factory = sqlite3.Row

        # Enable foreign key constraints and set the journal mode to Write-Ahead Logging (WAL) for better concurrency.
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")

        # The try-except-else-finally block ensures that the connection is properly managed
        try:
            yield connection
        except BaseException:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()


# Define a generic placeholder type named T that can
# be used to represent any type in the RowRepository class.
# This allows the repository to be typed for different models
# (this does not enforce types at runtime, just helps static type checkers and editors).
T = TypeVar("T")


class RowRepository(Generic[T]):
    """
    Repository for CRUD operations on a single SQLite table, typed to a specific model
    class with a specific table name using the Generic type system.
    """

    def __init__(
        self, database: SQLiteDatabase, model_type: type[T], table: str
    ) -> None:
        """
        Initialize the RowRepository instance with the provided database, model type, and table name.
        """

        self.database = database  # SQLiteDatabase instance that manages the connection to the SQLite database
        self.model_type = model_type  # dataclass type that represents the structure of the rows in the table
        self.table = table  # name of the table in the SQLite database that corresponds to the model
        self._model_columns = tuple(field.name for field in fields(model_type))

        # Gather a connection to the database and retrieve the schema metadata for the specified table.
        with self.database.connection() as connection:
            schema_columns = connection.execute(
                f"PRAGMA table_info({self.table})"
            ).fetchall()

        # Use the schema metadata to determine which columns are required (i.e., not nullable) for the specified table
        # and store them in the _required_columns attribute as a tuple of column names so that they can be used later for validation.
        self._required_columns = tuple(
            row["name"] for row in schema_columns if row["notnull"]
        )

    # * means that the following parameters are keyword-only, i.e. they must
    # be specified by name when calling the method.
    def list(
        self, *, limit: int = 100, order_by: str | None = None, order_dir: str = "ASC"
    ) -> list[T]:
        """
        List rows from the table, ordered by the specified column (or by id if not specified),
        and limited to the specified number of rows.
        """

        # Validate the parameters
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        # Determine the column to sort by. If order_by is not specified, use "id" if it exists in the model columns;
        # otherwise, use the first column in the model.
        sort_column = order_by or (
            "id" if "id" in self._model_columns else self._model_columns[0]
        )
        if (
            sort_column not in self._model_columns
        ):  # check that the specified sort column exists in the model columns
            raise ValueError(
                f"invalid order column: {sort_column} (column not found in model {self.model_type.__name__})"
            )

        # Validate the order direction. It must be either "ASC" or "DESC" (case-insensitive).
        order_dir = order_dir.upper()
        if order_dir not in ("ASC", "DESC"):
            raise ValueError(
                f"invalid order direction: {order_dir} (must be 'ASC' or 'DESC')"
            )

        # Gather a connection to the database, execute the constructed SQL query and return the rows as a list of model instances.
        with self.database.connection() as connection:
            rows = connection.execute(
                f"SELECT {', '.join(self._model_columns)} FROM {self.table} "
                f"ORDER BY {sort_column} {order_dir} LIMIT ?",
                (limit,),
            ).fetchall()

        return [self.model_type.from_row(row) for row in rows]  # type: ignore[attr-defined]
        # The previous comment suppresses static type-checker warning for the from_row method, the generic type T does not declare a from_row method even though the actual model is expected to provide one.

    def get(self, row_id: int) -> T | None:
        """
        Get a single row from the table by its id. Returns None if the row does not exist.
        """

        # Validate that the row_id is an integer and that the model has an "id" column.
        if not isinstance(row_id, int):
            raise TypeError("row_id must be an integer")
        if "id" not in self._model_columns:
            raise TypeError(f"{self.table} does not have a column named 'id'")

        # Gather a connection to the database, execute the constructed SQL query and return the row as a model instance or None if not found.
        with self.database.connection() as connection:
            row = connection.execute(
                f"SELECT {', '.join(self._model_columns)} FROM {self.table} WHERE id = ?",
                (row_id,),
            ).fetchone()

        return self.model_type.from_row(row) if row is not None else None  # type: ignore[attr-defined]
        # The previous comment suppresses static type-checker warning for the from_row method, the generic type T does not declare a from_row method even though the actual model is expected to provide one.

    def create(self, model: T, return_created: bool = False) -> T | None:
        """
        Create a new row in the table from the provided model instance.
        Returns the created model instance with its id set if return_created is True,
        otherwise returns None.
        If required columns are missing, raises a ValueError.
        """

        record = model.to_record()  # type: ignore[attr-defined]
        # The previous comment suppresses static type-checker warning for the to_record method, the generic type T does not declare a to_record method even though the actual model is expected to provide one.

        missing_columns = [
            column for column in self._required_columns if record.get(column) is None
        ]
        if missing_columns:
            raise ValueError(
                f"cannot create a {self.table} row; required columns are missing: "
                f"{', '.join(missing_columns)}"
            )

        # Optional None values are omitted so SQLite can apply a column default.
        record = {key: value for key, value in record.items() if value is not None}

        # Prepare the SQL query for inserting the new row into the table.
        # The columns and placeholders are constructed from the record dictionary.
        columns = ", ".join(record)
        placeholders = ", ".join(f":{column}" for column in record)

        with self.database.connection() as connection:
            cursor = connection.execute(
                f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})",
                record,
            )
            if return_created:
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

        if return_created and row is None:
            raise LookupError(f"{self.table} row {cursor.lastrowid} does not exist")

        if return_created:
            return self.model_type.from_row(row)  # type: ignore[attr-defined]
            # The previous comment suppresses static type-checker warning for the from_row method, the generic type T does not declare a from_row method even though the actual model is expected to provide one.
        else:
            return None

    def update(self, model: T) -> T:
        record = model.to_record()  # type: ignore[attr-defined]
        # The previous comment suppresses static type-checker warning for the to_record method, the generic type T does not declare a to_record method even though the actual model is expected to provide one.

        row_id = getattr(model, "id", None)
        if row_id is None:
            raise ValueError("update requires a model with an id")
        record = {key: value for key, value in record.items() if key != "id"}
        assignments = ", ".join(f"{column} = :{column}" for column in record)
        record["id"] = row_id
        with self.database.connection() as connection:
            connection.execute(
                f"UPDATE {self.table} SET {assignments} WHERE id = :id", record
            )
            row = connection.execute(
                f"SELECT {', '.join(self._model_columns)} FROM {self.table} WHERE id = :id",
                record,
            ).fetchone()
        if row is None:
            raise LookupError(f"{self.table} row {row_id} does not exist")
        return self.model_type.from_row(row)  # type: ignore[attr-defined]
        # The previous comment suppresses static type-checker warning for the from_row method, the generic type T does not declare a from_row method even though the actual model is expected to provide one.

    def delete(self, row_id: int) -> bool:
        with self.database.connection() as connection:
            cursor = connection.execute(
                f"DELETE FROM {self.table} WHERE id = ?", (row_id,)
            )
        return cursor.rowcount > 0

    def delete_where(self, **filters: object) -> bool:
        if not filters or any(column not in self._model_columns for column in filters):
            raise ValueError("delete_where requires valid model columns")
        clauses = " AND ".join(f"{column} = :{column}" for column in filters)
        with self.database.connection() as connection:
            cursor = connection.execute(
                f"DELETE FROM {self.table} WHERE {clauses}", filters
            )
        return cursor.rowcount > 0


# It inherits from the generic RowRepository class, which provides common CRUD operations
# for any table in the database.
# This class then adds additional methods specific to the "food_entries" table and provides wrapper methods
# for common CRUD opearations for convenience and clearer code.
# The FoodEntryRepository is specifically typed to handle FoodEntry model
# instances and operates on the "food_entries" table.
class FoodEntryRepository(RowRepository[FoodEntry]):
    """Repository for historical food diary rows."""

    # * means that the following parameters are keyword-only, i.e. they must
    # be specified by name when calling the constructor.
    def __init__(
        self,
        database: SQLiteDatabase | Path,
        *,
        schema_path: Path = DEFAULT_SCHEMA_PATH,
    ) -> None:
        if not isinstance(database, SQLiteDatabase):
            database = SQLiteDatabase(database, schema_path)
        super().__init__(database, FoodEntry, "food_entries")

    # * means that the following parameters are keyword-only, i.e. they must
    # be specified by name when calling the method.
    def list_food_entries(self, *, limit: int = 25) -> list[FoodEntry]:
        """
        List the most recent food diary entries, ordered by occurred_on, created_at, and id descending.
        """
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
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM food_entries"
            ).fetchone()
        return int(row["count"])

    # * means that the following parameters are keyword-only, i.e. they must
    # be specified by name when calling the method.
    def create_food_entry(
        self, entry: FoodEntry, *, return_created: bool = True
    ) -> FoodEntry | None:
        return self.create(entry, return_created=return_created)  # type: ignore[return-value]

    def delete_food_entry(self, entry_id: int) -> bool:
        return self.delete(entry_id)

    def seed_if_empty(self, entries: Iterable[FoodEntry]) -> None:
        if self.count_food_entries() > 0:
            return
        for entry in entries:
            self.create(entry)


# TODO: Add more specific repositories for other tables if needed, following the same pattern as FoodEntryRepository.


class Storage:
    """
    Assembles all typed repositories (generic and specific subclasses) into one object for easy access.
    """

    def __init__(
        self, database_path: Path, *, schema_path: Path = DEFAULT_SCHEMA_PATH
    ) -> None:

        # Initialize the SQLiteDatabase instance with the provided database and schema paths.
        # This instance will then be passed to each RowRepository to manage the connection to the SQLite database.
        database = SQLiteDatabase(database_path, schema_path)

        # Initialize RowRepository instances for each table in the Garum schema,
        # specifying the corresponding model type and table name.
        # These repositories will be used to perform CRUD operations on the respective tables.

        # As to not write a block of underable code the parameters are not specified in each
        # RowRepository constructor, but they follow this pattern:
        # RowRepository(database, ModelType, "table_name_in_the_database")

        # The parameters for each RowRepository are as follows:
        # database is the SQLiteDatabase instance that manages the connection to the SQLite database.
        # ModelType is the dataclass that represents the structure of the rows in the table (coming from models.py)
        # table_name_in_the_database is the name of the table in the SQLite database that corresponds to the model.

        self.brands = RowRepository(database, Brand, "brands")
        self.categories = RowRepository(database, Category, "categories")
        self.units = RowRepository(database, Unit, "units")
        self.sources = RowRepository(
            database, NutritionRecommendationSource, "nutrition_recommendation_sources"
        )
        self.foods = RowRepository(database, Food, "foods")
        self.food_categories = RowRepository(database, FoodCategory, "food_categories")
        self.nutrient_profiles = RowRepository(
            database, NutrientProfile, "nutrient_profiles"
        )
        self.nutrients = RowRepository(database, Nutrient, "nutrients")
        self.nutrient_values = RowRepository(database, NutrientValue, "nutrient_values")
        self.consumptions = RowRepository(database, Consumption, "consumptions")
        self.suggested_frequencies = RowRepository(
            database, SuggestedFrequency, "suggested_frequencies"
        )
        self.recipes = RowRepository(database, Recipe, "recipes")
        self.recipe_ingredients = RowRepository(
            database, RecipeIngredient, "recipe_ingredients"
        )
        self.inventory = RowRepository(database, Inventory, "inventory")
        self.food_entries = FoodEntryRepository(database)
        self.stores = RowRepository(database, Store, "stores")
        self.store_items = RowRepository(database, StoreItem, "store_items")
        self.price_history = RowRepository(database, PriceHistory, "price_history")
        self.grocery_bills = RowRepository(database, GroceryBill, "grocery_bills")
        self.purchases = RowRepository(database, Purchase, "purchases")
