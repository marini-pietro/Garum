"""Shared application services necessary to the GUI code."""

# First party import
from dataclasses import dataclass

# Local imports
from garum.handlers.analytics_handler import AnalyticsHandler
from garum.handlers.storage_handler import StorageHandler


# Data class to hold the shared services for the GUI pages
# The @dataclass decorator automatically generates special methods like __init__() and __repr__() for the class, 
# frozen=True makes the instances of this class immutable, meaning that once an instance is created, its attributes cannot be modified.
@dataclass(frozen=True)
class GuiServices:
    """Dependencies shared by GUI pages."""

    storage: StorageHandler
    analytics: AnalyticsHandler
