"""Parsing utilities for CVE year ranges and blacklist patterns.

This module provides functions to:
    - Generate regex patterns for year ranges.
    - Generate regex patterns for blacklisted keywords.
    - Parse and validate year range arguments for CVE filtering.
"""

import re
from datetime import datetime

import typer
from rich import print as pprint
from typing_extensions import Optional

from poc_champ.constants import PREFIX, SEARCH_ENGINE_EXCLUDE_ENDPOINTS


def set_range_pattern(min_year: int = 0, max_year: int = 0) -> str:
    """
    Generate a regex pattern for an allowed year frame.

    :param min_year int: Minimum year in the timeframe. Defaults to 0.
    :param max_year int: Maximum year in the timeframe. Defaults to 0.
    :returns: Regex pattern for filtering CVEs by year.
    :rtype: str

    .. note::
        If no arguments are provided, a default timeframe of the last 5 years is generated.
    """
    if not max_year and not min_year:
        interval = 5
        max_year = datetime.now().year
        min_year = max_year - interval

    year_range = range(min_year, max_year + 1)
    return "|".join([str(year) for year in year_range])


def get_blacklisted_paterns() -> str:
    """
    Generate a regex pattern of blacklisted keywords for links to exclude.

    :returns: Regex pattern for blacklisted endpoints.
    :rtype: str
    """
    blacklist_pattern = "|".join(SEARCH_ENGINE_EXCLUDE_ENDPOINTS)
    return blacklist_pattern


def parse_year_range(year_argument: Optional[str]) -> str:
    """
    Parse and validate a year frame argument, then generate a regex pattern.

    :param year_argument str: Raw argument of year range.
    :returns: Regex pattern for allowed year frame.
    :rtype: str
    :raises typer.Exit: If the argument is invalid.
    """
    # If no argument - resolve as default, with no params
    if not year_argument:
        return set_range_pattern()

    # If matches regex pattern <year>-<year>
    if re.match(r"^\d{4}-\d{4}$", year_argument):
        year_range = year_argument.split("-")
        year_interval = int(year_range[1]) - int(year_range[0])

        if year_interval < 0:
            pprint(f"[bold red]{PREFIX}Invalid year range format.")
            raise typer.Exit()

        year_min = int(year_range[0])
        year_max = int(year_range[1])

    # If matches regex pattern <year>
    elif re.match(r"^\d{4}$", year_argument):
        year_min = int(year_argument)
        year_max = int(year_argument)

    # Other cases are treated as invalid formats
    else:
        pprint(f"[bold red]{PREFIX}Invalid year range format.")
        raise typer.Exit()

    return set_range_pattern(year_min, year_max)
