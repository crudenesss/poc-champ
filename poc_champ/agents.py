"""
Agents module for CVE and repository search.

This module provides functions to request CVE identifiers from cve.org
and to search for related GitHub repositories using a search engine.

Functions:
    - request_cves: Search for CVEs by keyword and year range.
    - request_repositories: Search for GitHub repositories related to a CVE.
"""

import re

from rich import print as pprint
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from poc_champ.utils.render import parse_javascript_page
from poc_champ.constants import (
    PREFIX,
    CVE_ORG_ENDPOINT,
    CVE_ORG_BTN_CLASS,
    CVE_ORG_SEARCH_PARAM,
    SEARCH_ENGINE_ENDPOINT,
    SEARCH_ENGINE_PARAM,
    SEARCH_ENGINE_BTN_CLASS,
    SEARCH_ENGINE_EXPAND_ITER,
    SEARCH_ENGINE_EXCLUDE_ENDPOINTS
)


def request_cves(keyword: str, year_range: str) -> list:
    """
    Send request to `cve.org` to get HTML response to parse.

    :param keyword: Keywords to search for related CVEs.
    :type keyword: str
    :param year_range: Regex pattern of allowed year frame.
    :type year_range: str

    :returns: List of CVEs parsed from HTML response.
    :rtype: list
    """
    # Assemble and send request to cve.mitre.org
    pprint(
        f"[bright_blue]{PREFIX}Searching by keywords: [bold]{keyword}[/bold]...[/bright_blue]"
    )
    sources = parse_javascript_page(
        CVE_ORG_ENDPOINT,
        param=CVE_ORG_SEARCH_PARAM,
        query=keyword,
        load_element=(By.TAG_NAME, "h2"),
        paginate={"action": "next", "interact": (By.CLASS_NAME, CVE_ORG_BTN_CLASS)},
    )

    # Send html response to parsing function
    cve_list = []
    for response in sources:
        # Find table with CVE in html response
        bs = BeautifulSoup(response, features="lxml")

        # From all CVE's, retrieve such that match provided year frame.
        # Note: CVE-<year>-<code> is the format of CVE ID's.
        for row in bs.find_all("a"):
            if not row.string:
                continue
            if re.match(rf"\bCVE-({year_range})-\d{{4,}}\b", row.string):
                cve_list.append(row.string)

    return cve_list


def request_repositories(cve: str) -> list:
    """
    Search for GitHub repositories related to a given CVE.

    :param cve: CVE identifier to search for.
    :type cve: str

    :returns: List of GitHub repository URLs related to the CVE.
    :rtype: list
    """

    def get_blacklisted_paterns() -> str:
        """
        Generate a regex pattern of blacklisted keywords for links to exclude.

        :returns: Regex pattern for blacklisted endpoints.
        :rtype: str
        """
        blacklist_pattern = "|".join(SEARCH_ENGINE_EXCLUDE_ENDPOINTS)
        return blacklist_pattern

    sources = parse_javascript_page(
        SEARCH_ENGINE_ENDPOINT,
        param=SEARCH_ENGINE_PARAM,
        query=f'"{cve}"',
        load_element=(By.TAG_NAME, "section"),
        dork="site:github.com",
        paginate={
            "action": "expand",
            "interact": (By.ID, SEARCH_ENGINE_BTN_CLASS),
            "iterations": SEARCH_ENGINE_EXPAND_ITER,
        },
    )

    if not sources:
        return []

    cve_poc = []

    # Retrieve blacklisted keywords to filter
    pattern = get_blacklisted_paterns()

    # Parse Github links
    for page in sources:
        bs = BeautifulSoup(page, features="lxml")
        links = bs.find_all("a", attrs={"data-testid": "result-title-a"})

        for link in links:
            try:
                # Add to result only if it is just a clean repository link
                if (
                    not re.findall(pattern, link["href"])
                    and len(re.findall(r"\/", link["href"])) > 3
                ):
                    cve_poc.append(link["href"])
            except KeyError:
                continue

    return cve_poc
