"""
utils.py
--------
Small utility helpers for the CO₂ Dashboard. Kept intentionally tiny.
"""

from typing import List
import pandas as pd


def safe_html(html: str):
    """
    Small wrapper for Shiny UI HTML output.
    Kept as a function to make testing easier.
    """
    try:
        from shiny import ui
        return ui.HTML(html)
    except Exception:
        # If Shiny is not available (e.g., during some tests), return raw string.
        return html


def get_country_list(df: pd.DataFrame) -> List[str]:
    """
    Return a sorted list of unique country names.
    Note: we keep it simple — for very large datasets, caching would be better.
    """
    return sorted(df["country"].unique())
