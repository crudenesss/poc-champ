"""Contains parsing fuctions"""

import re
import os
import json
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
    r"""Parse argument of year frame to validate it and 
    sent to `set_range_pattern()` function.

    ## Parameters:
        **year_argument** (_str_): 
        Raw argument of year range.

    ### Raises:
        `typer.Abort`: 
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
            rich_print("Invalid year range format.")
            raise typer.Abort()

        year_min = int(year_range[0])
        year_max = int(year_range[1])

    # If matches regex pattern <year>
    elif re.match(r"^\d{4}$", year_argument):
        year_min = int(year_argument)
        year_max = int(year_argument)

    # Other cases are trated as invalid formats
    else:
        rich_print("Invalid year range format.")
        raise typer.Abort()

    return set_range_pattern(year_min, year_max)


def parse_cve_response(html_content, year_range):
    """Parse html content of response from `cve.mitre.org` to extract CVE's
    of provided time frame. 

    ## Parameters:
        **html_content** (_str_): raw html string.
        **year_range** (_str_): REGEX pattern of year time frame.

    ### Returns:
        _list_: 
        CVE's parsed from html response.
    """

    # Find table with CVE in html response
    bs = BeautifulSoup(html_content, features="html.parser")
    cve_table = bs.find("div", id="TableWithRules")

    cve_list = []

    # From all CVE's, retrieve such that match provided year frame.
    # Note: CVE-<year>-<code> is the format of CVE ID's.
    for row in cve_table.find_all("a"):
        if re.match(rf"\bCVE-({year_range})-\d{{4,}}\b", row.string):
            cve_list.append(row.string)

    return cve_list


def request_cves(keyword, year_range):
    """Send request to `cve.mitre.org` to get html response to parse.

    ## Parameters:
        **keyword** (_str_): keywords to search for related CVE's.
        **year_range** (_str_): raw year frame argument from CLI.

    ### Raises:
        `typer.Exit`: graceful exit in case request goes wrong.

    ### Returns:
        _list_: 
        CVE's parsed from html response.
    """

    # Retrieve years to filter cve's by
    year_range_pattern = parse_year_range(year_range)

    # Assemble and send request to cve.mitre.org
    rich_print(f"Searching by keywords: {keyword}...")
    keywords_prepared = re.sub(" ", "+", keyword, count=-1)
    response = requests.get(
        CVE_MITRE_LINK,
        params={"keyword": keywords_prepared},
        timeout=10,
    )

    # If request was somehow unsuccessful
    if response.status_code != 200:
        rich_print(
            """Oops! Something went wrong =(
            Try checking internet connection"""
        )
        raise typer.Exit()

    # Send html response to parsing function
    cve_list = parse_cve_response(response.text, year_range_pattern)
    return cve_list


def request_from_duckduckgo(query):
    """Send request to DuckDuck Go search engine to retrieve Github links to repositories.

    ## Parameters:
        **query** (_str_): CVE ID string.

    ### Returns:
        _list_: 
        Available Github links to repositories.
    """

    # Configure browser instance to run on background (without GUI)
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    # Start Firefox browser instance
    browser = webdriver.Firefox(options=options)

    # Send request to browser to find Github repos for CVE
    browser.get(f'{SEARCH_DUCKDUCKGO_ENDPOINT}?q="{query}" site:github.com')

    # Try retrieving more if search engine has more than one page result
    try:
        link = browser.find_element(By.ID, "more-results")
        link.click()
    except NoSuchElementException:
        pass
    # Render all the JavaScript stuff and close browser instances
    finally:
        html = browser.page_source
        browser.close()

    results = []

    # Parse Github links
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", attrs={"data-testid": "result-title-a"})

    # Retrieve blacklisted keywords to filter
    pattern = get_blacklisted_paterns()

    for link in links:
        try:
            # Add to result only if it is just a clean repository link
            if (
                not re.findall(pattern, link["href"])
                and len(re.findall(r"\/", link["href"])) > 3
            ):
                results.append(link["href"])
        except KeyError:
            continue

    return results


def set_filename(filename, index):
    if not re.findall(r"\.", filename):
        return f"{filename}-{str(index)}"
    else:
        filename_parts = filename.split(".")
        filename_parts[0] += f"-{str(index)}"
        return ".".join(filename_parts)


def output_file(filename, result):
    if os.path.exists(f"./output/{filename}"):
        rich_print(f"[yellow]Output file {filename} already exists.[/yellow]")
        i = 1
        while os.path.exists(f"./output/{set_filename(filename, i)}"):
            i += 1
        filename = f"{set_filename(filename, i)}"

    with open(f"output/{filename}", "w", encoding="utf-8") as file:
        file.write(json.dumps(result, indent=2))

    return filename
