"""Contains parsing fuctions"""

import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from rich import print as rich_print
import typer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from poc_champ.constants import SEARCH_DUCKDUCKGO_ENDPOINT, CVE_MITRE_LINK


def set_range_pattern(min_year=None, max_year=None):

    if not max_year and not min_year:
        interval = 5
        max_year = datetime.now().year
        min_year = max_year - interval

    year_range = range(min_year, max_year + 1)
    return "|".join([str(year) for year in year_range])


def get_blacklisted_paterns():

    blacklist = [
        "actions",
        "activity",
        "advisories",
        "blob",
        "issues",
        "milestones",
        "projects",
        "pull",
        "pulls",
        "releases",
        "security",
        "topics",
        r"\/$",
        r"\?",
    ]

    blacklist_pattern = "|".join(blacklist)
    return blacklist_pattern


def parse_year_range(year_argument):

    if not year_argument:
        return set_range_pattern()

    if re.match(r"^\d{4}-\d{4}$", year_argument):
        year_range = year_argument.split("-")
        year_interval = int(year_range[1]) - int(year_range[0])

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


def parse_cve_response(html_content, year_range):

    bs = BeautifulSoup(html_content, features="html.parser")
    cve_table = bs.find("div", id="TableWithRules")

    cve_list = []

    for row in cve_table.find_all("a"):
        if re.match(rf"\bCVE-({year_range})-\d{{4,}}\b", row.string):
            cve_list.append(row.string)

    return cve_list


def request_cves(keyword, year_range):

    # Retrieve years to filter cve's by
    year_range_pattern = parse_year_range(year_range)

    rich_print(f"Searching by keywords: {keyword}...")
    keywords_prepared = re.sub(" ", "+", keyword, count=-1)
    response = requests.get(
        CVE_MITRE_LINK,
        params={"keyword": keywords_prepared},
        timeout=10,
    )
    if response.status_code != 200:
        rich_print(
            """Oops! Something went wrong =(
            Try checking internet connection"""
        )
        raise typer.Exit()

    cve_list = parse_cve_response(response.text, year_range_pattern)
    return cve_list


def request_from_duckduckgo(query):

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)

    browser.get(f'{SEARCH_DUCKDUCKGO_ENDPOINT}?q="{query}" site:github.com')

    try:
        link = browser.find_element(By.ID, "more-results")
        link.click()
    except NoSuchElementException:
        pass
    finally:
        html = browser.page_source
        browser.close()

    results = []

    soup = BeautifulSoup(html, "html.parser")

    links = soup.find_all("a", attrs={"data-testid": "result-title-a"})

    pattern = get_blacklisted_paterns()

    for link in links:

        try:
            if (
                not re.findall(pattern, link["href"])
                and len(re.findall(r"\/", link["href"])) > 3
            ):
                results.append(link["href"])
        except KeyError:
            continue

    return results
