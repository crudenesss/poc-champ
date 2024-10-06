"""Contains parsing fuctions"""

import re
from datetime import datetime
from bs4 import BeautifulSoup
from rich import print as rich_print
import typer


def set_range_pattern(min_year=None, max_year=None):

    if not max_year and not min_year:
        interval = 5
        max_year = datetime.now().year
        min_year = max_year - interval

    year_range = range(min_year, max_year+1)
    return "|".join([str(year) for year in year_range])


def parse_year_range(year_argument):

    if not year_argument:
        return set_range_pattern()

    if re.match(r"^\d{4}-\d{4}$", year_argument):
        year_range = year_argument.split("-")
        year_interval = int(year_range[1])-int(year_range[0])

        if year_interval < 0:
            rich_print("Invalid year range format.")
            raise typer.Abort()

        year_min = int(year_range[0])
        year_max = int(year_range[1])

    elif re.match(r"^\d{4}$", year_argument):
        year_min = int(year_argument)
        year_max = int(year_argument)

    else:
        rich_print("Invalid year range format.")
        raise typer.Abort()

    return set_range_pattern(year_min, year_max)


def parse_response(html_content, year_range):

    rich_print(year_range)

    bs = BeautifulSoup(html_content, features="html.parser")
    cve_table = bs.find("div", id="TableWithRules")

    cve_list = []

    for row in cve_table.find_all("a"):
        if re.match(rf"\bCVE-({year_range})-\d{{4,}}\b", row.string):
            cve_list.append(row.string)

    return cve_list
