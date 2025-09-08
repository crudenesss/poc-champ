"""Contains parsing fuctions"""

import re
from datetime import datetime

import typer
from rich import print as pprint

from poc_champ.constants import PREFIX, SEARCH_ENGINE_EXCLUDE_ENDPOINTS

def set_range_pattern(min_year=0, max_year=0):
    """Generate REGEX pattern for allowed year frame.

    ## Parameters:
        **min_year** (_int_, optional): 
        Min year in given timeframe. Defaults to None. <br>

        **max_year** (_int_, optional): 
        Min year in given timeframe. Defaults to None.

    ### Returns:
        _str_: REGEX pattern for filtering CVE's. 
        **Note:** If no arguments were provided, default timeframe of the last
        5 years will be generated.
    """

    if not max_year and not min_year:
        interval = 5
        max_year = datetime.now().year
        min_year = max_year - interval

    year_range = range(min_year, max_year + 1)
    return "|".join([str(year) for year in year_range])


def get_blacklisted_paterns():
    """Generate REGEX pattern of blacklisted keywords for links to exclude.

    ### Returns:
        _str_: REGEX pattern.
    """

    blacklist_pattern = "|".join(SEARCH_ENGINE_EXCLUDE_ENDPOINTS)
    return blacklist_pattern


def parse_year_range(year_argument):
    r"""Parse argument of year frame to validate it and 
    sent to `set_range_pattern()` function.

    ## Parameters:
        **year_argument** (_str_): 
        Raw argument of year range.

    ### Raises:
        `typer.Exit`: 
        Graceful quit in case invalid argument were brought.

    ### Returns:
        `set_range_pattern`: value of function.
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

    # Other cases are trated as invalid formats
    else:
        pprint(f"[bold red]{PREFIX}Invalid year range format.")
        raise typer.Exit()

    return set_range_pattern(year_min, year_max)
