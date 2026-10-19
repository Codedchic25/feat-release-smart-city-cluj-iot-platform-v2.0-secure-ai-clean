"""Smart City Cluj Application Multipage Visual Interface Bundle."""

from __future__ import annotations

import importlib
from typing import Any


def _load_dynamic_page_component(module_string_name: str, class_string_target: str) -> Any:
    """Safely load and extract components from modules starting with numeric prefixes."""
    try:
        execution_package = importlib.import_module(f"pages.{module_string_name}")
        return getattr(execution_package, class_string_target)
    except (ImportError, AttributeError):
        return None


# Dynamically resolve and bind the obscured component definitions
DashboardPage: Any = _load_dynamic_page_component("1_Dashboard", "DashboardPage")
AnalyticsPage: Any = _load_dynamic_page_component("2_Analytics", "AnalyticsPage")
SettingsPage: Any = _load_dynamic_page_component("3_Settings", "SettingsPage")
AboutPage: Any = _load_dynamic_page_component("4_About", "AboutPage")

__all__ = [
    "AnalyticsPage",
    "DashboardPage",
    "AboutPage",
    "SettingsPage",
]
