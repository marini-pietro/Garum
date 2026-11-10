"""Shared application services used by the GUI."""

from dataclasses import dataclass

from garum.handlers.analytics_handler import AnalyticsHandler
from garum.handlers.storage_handler import StorageHandler


@dataclass(frozen=True)
class GuiServices:
    """Dependencies shared by GUI pages."""

    storage: StorageHandler
    analytics: AnalyticsHandler
