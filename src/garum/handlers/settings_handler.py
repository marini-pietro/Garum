"""Loading, validating, and saving user preferences."""

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SETTINGS_FILE = PROJECT_ROOT / "settings.json"

valid_settings: dict[str, list[str] | callable | int | float] = {
    "APP_THEME": ["light", "dark"],
    "APP_LANGUAGE": ["en", "it"],
    "MEASUREMENT_SYSTEM": ["metric", "imperial"],
    "USER_WEIGHT": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0,
    "USER_HEIGHT": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0,
    "USER_AGE": lambda value: isinstance(value, int) and not isinstance(value, bool) and value > 0,
    "USER_SEX": ["male", "female", "other"],
    "USER_ACTIVITY_LEVEL": [
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extra_active",
    ],
}

settings_defaults: dict[str, str | int | float] = {
    "APP_THEME": "light",
    "APP_LANGUAGE": "en",
    "MEASUREMENT_SYSTEM": "metric",
    "USER_WEIGHT": 70.0,
    "USER_HEIGHT": 170.0,
    "USER_AGE": 30,
    "USER_SEX": "male",
    "USER_ACTIVITY_LEVEL": "moderately_active",
}

settings: dict[str, str | int | float] = {}

def validate_setting(key: str, value: Any) -> Any:
    """
    Validate a setting value based on its key.
    Returns ValueError if the key is unknown.

    Args:
        key (str): The setting key to validate.
        value (Any): The value to validate.
    
    Returns:
        The value if its valid, or the default value for that setting if the value is invalid.
    """

    if key not in valid_settings:
        raise ValueError(f"Unknown setting: {key}")

    valid_values = valid_settings[key]
    if isinstance(valid_values, list):
        if value not in valid_values:
            return settings_defaults[key]
    elif callable(valid_values):
        if not valid_values(value):
            return settings_defaults[key]

    return value


def load_settings(path: Path = SETTINGS_FILE) -> dict[str, str | int | float]:
    """
    Load settings from a JSON file and validate them against the defined valid settings.
    If the file does not exist, it will be created with default settings.
    """
    
    # Initialize the settings dictionary
    loaded_settings: dict[str, Any] = {}

    # Load settings from the file if it exists
    if path.exists():
        with path.open("r", encoding="utf-8") as settings_file:
            data = json.load(settings_file)
        if not isinstance(data, dict):
            raise ValueError(f"Settings file must contain a JSON object: {path}")
        loaded_settings = data
    else:
        # If the settings file does not exist, create it with default settings
        settings.update(settings_defaults)
        save_settings(path)

    # Gather the settings from the file that do not appear in the defaults
    unknown_settings = set(loaded_settings) - set(settings_defaults)
    if unknown_settings: # If there is at least one unknown setting, raise a ValueError
        unknown = ", ".join(sorted(unknown_settings))
        raise ValueError(f"Unknown settings in {path}: {unknown}")

    # settings_defaults | loaded_settings creates a copy of the defaults
    # settings and then ovewrite in it each setting that is present in the loaded settings
    # with the value from the loaded settings.
    # This way we do not require the settings file to contain all the settings, 
    # and we can add new settings in the future without breaking existing settings files.
    # We then build the validated_settings dictionary by validating each setting in the merged dictionary.
    # This is necessary because the loaded settings may contain settings with an already present key
    # but an invalid value, and we want to replace those with the default value for that setting.
    validated_settings = {
        key: validate_setting(key, value)
        for key, value in (settings_defaults | loaded_settings).items()
    }

    settings.clear() # Clear the global settings dictionary to remove any previous settings
    settings.update(validated_settings) # Update the global settings dictionary with the validated settings
    return settings.copy()


def save_settings(
    path: Path = SETTINGS_FILE,
) -> None:
    """
    Save current settings to a JSON file.
    If no path is provided, it will save to the default settings file.
    If a path is provided, it will save to that path instead (for exporting settings).
    """
 
    with path.open("w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=4)
