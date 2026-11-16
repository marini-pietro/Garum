"""Calculate personalized nutrition targets from database recommendations."""

from collections.abc import Mapping
from datetime import date

from garum.handlers.storage_handler import StorageHandler

ACTIVITY_FACTORS: dict[str, float] = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}


class AnalyticsHandler:
    """Calculate daily energy and nutrient targets for the current user."""

    def __init__(
        self,
        storage: StorageHandler,
        user_settings: Mapping[str, str | int | float],
    ) -> None:
        self.storage = storage
        self.user_settings = user_settings
        self.daily_reference_values = self.calculate_daily_reference_values(
            user_settings
        )

    def calculate_daily_reference_values(
        self,
        user_settings: Mapping[str, str | int | float],
    ) -> dict[str, float]:
        """Return daily targets keyed by nutrient code."""

        bmr = self.calculate_bmr(user_settings)
        activity_level = str(user_settings["USER_ACTIVITY_LEVEL"])

        try:
            calories = bmr * ACTIVITY_FACTORS[activity_level]
        except KeyError as error:
            raise ValueError(f"Unknown activity level: {activity_level}") from error

        daily_values = {"kcals": round(calories, 2)}
        weight = float(user_settings["USER_WEIGHT"])
        nutrients = {
            nutrient.id: nutrient.code
            for nutrient in self.storage.nutrients.list(limit=100)
        }
        for goal in self.storage.daily_nutrition_goals.list(limit=100):
            nutrient_code = nutrients.get(goal.nutrient_type_id)
            if nutrient_code is not None:
                daily_values[nutrient_code] = round(goal.amount_per_kg * weight, 2)

        return daily_values

    def calculate_daily_nutrients(self, today: date | None = None) -> dict[str, float]:
        """Return nutrient totals for all food and recipe entries consumed today."""

        consumed = {
            nutrient.code: 0.0 for nutrient in self.storage.nutrients.list(limit=100)
        }
        target_date = today or date.today()

        for entry in self.storage.consumptions.list_consumptions(limit=10000):
            if entry.occurred_on != target_date:
                continue
            if entry.food_id is not None and entry.quantity is not None:
                nutrients = self._calculate_food_nutrients(
                    entry.food_id, entry.quantity, entry.unit_id
                )
            elif entry.recipe_id is not None:
                recipe = self.storage.recipes.get(entry.recipe_id)
                if recipe is None:
                    continue
                servings = entry.quantity or 1.0
                nutrients = {
                    code: amount * servings / recipe.servings
                    for code, amount in self.storage.calculate_recipe_nutrients(
                        entry.recipe_id
                    ).items()
                }
            else:
                continue

            for code, amount in nutrients.items():
                consumed[code] = consumed.get(code, 0.0) + amount

        return {code: round(amount, 2) for code, amount in consumed.items()}

    def calculate_daily_macronutrient_amounts(
        self, today: date | None = None
    ) -> dict[str, float]:
        """Return today's consumed amounts for macronutrients."""

        consumed = self.calculate_daily_nutrients(today)
        return {
            nutrient.code: consumed.get(nutrient.code, 0.0)
            for nutrient in self.storage.nutrients.list(limit=100)
            if nutrient.type == "macronutrient"
            and self.daily_reference_values.get(nutrient.code, 0.0) > 0
        }

    def _calculate_food_nutrients(
        self, food_id: int, quantity: float, unit_id: int | None
    ) -> dict[str, float]:
        """Calculate nutrients for a quantity of one food."""

        if unit_id is None:
            return {}
        with self.storage.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT nutrient.code, food_nutrient.amount,
                       base.basis_quantity, basis_unit.kind AS basis_kind,
                       basis_unit.code AS basis_code,
                       consumed_unit.kind AS consumed_kind,
                       consumed_unit.code AS consumed_code
                FROM food_nutrient_bases AS base
                JOIN food_nutrients AS food_nutrient
                    ON food_nutrient.food_id = base.food_id
                   AND food_nutrient.base_id = base.id
                JOIN nutrients AS nutrient
                    ON nutrient.id = food_nutrient.nutrient_type_id
                JOIN units AS basis_unit ON basis_unit.id = base.basis_unit_id
                JOIN units AS consumed_unit ON consumed_unit.id = ?
                WHERE base.food_id = ?
                  AND basis_unit.kind = consumed_unit.kind
                """,
                (unit_id, food_id),
            ).fetchall()

        def scale(code: str, unit_kind: str) -> float:
            if unit_kind == "mass" and code == "kg":
                return 1000.0
            if unit_kind == "volume" and code == "l":
                return 1000.0
            return 1.0

        return {
            row["code"]: float(row["amount"])
            * quantity
            * scale(row["consumed_code"], row["consumed_kind"])
            / (
                float(row["basis_quantity"])
                * scale(row["basis_code"], row["basis_kind"])
            )
            for row in rows
        }

    def calculate_bmr(self, user_settings: Mapping[str, str | int | float]) -> float:
        """Calculate the Basal Metabolic Rate (BMR) for the user using the Mifflin-St Jeor equation."""

        # Extract user parameters
        weight = float(user_settings["USER_WEIGHT"])
        height = float(user_settings["USER_HEIGHT"])
        age = int(user_settings["USER_AGE"])
        sex = str(user_settings["USER_SEX"])

        # Validate measurement system (the following calculation assumes metric units)
        if str(user_settings.get("MEASUREMENT_SYSTEM", "metric")) != "metric":
            raise ValueError(
                "Only metric measurements are currently supported for BMR calculation."
            )

        if sex == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif sex == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            male_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            female_bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            bmr = (male_bmr + female_bmr) / 2

        return bmr
