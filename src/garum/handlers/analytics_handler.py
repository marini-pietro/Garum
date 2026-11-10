"""Calculate personalized nutrition targets from database recommendations."""

from collections.abc import Mapping

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
        weight = float(user_settings["USER_WEIGHT"])
        height = float(user_settings["USER_HEIGHT"])
        age = int(user_settings["USER_AGE"])
        sex = str(user_settings["USER_SEX"])
        activity_level = str(user_settings["USER_ACTIVITY_LEVEL"])

        if str(user_settings.get("MEASUREMENT_SYSTEM", "metric")) != "metric":
            raise ValueError("Only metric measurements are currently supported")

        if sex == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif sex == "female":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            male_bmr = 10 * weight + 6.25 * height - 5 * age + 5
            female_bmr = 10 * weight + 6.25 * height - 5 * age - 161
            bmr = (male_bmr + female_bmr) / 2

        try:
            calories = bmr * ACTIVITY_FACTORS[activity_level]
        except KeyError as error:
            raise ValueError(f"Unknown activity level: {activity_level}") from error

        daily_values = {"kcals": round(calories, 2)}
        nutrients = {
            nutrient.id: nutrient.code
            for nutrient in self.storage.nutrients.list(limit=100)
        }
        for goal in self.storage.daily_nutrition_goals.list(limit=100):
            nutrient_code = nutrients.get(goal.nutrient_type_id)
            if nutrient_code is not None:
                daily_values[nutrient_code] = round(goal.amount_per_kg * weight, 2)

        return daily_values
