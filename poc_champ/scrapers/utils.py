"""Miscellaneous utility functions for scrapers."""

from typing import Any


def build_query(endpoint: str, param: str, query: str, **kwargs: Any) -> str:
    """Build a search query URL with optional parameters."""
    dork = kwargs.get("dork", "")
    return f"{endpoint}?{param}={query} {dork}".strip()
