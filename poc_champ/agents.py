""""""

import re

from rich import print as pprint
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from poc_champ.utils.render import parse_javascript_page
from poc_champ.utils.parser import get_blacklisted_paterns
from poc_champ.constants import (
    PREFIX,
    CVE_ORG_ENDPOINT,
    CVE_ORG_BTN_CLASS,
    CVE_ORG_SEARCH_PARAM,
    SEARCH_ENGINE_ENDPOINT,
    SEARCH_ENGINE_PARAM,
    SEARCH_ENGINE_BTN_CLASS,
    SEARCH_ENGINE_EXPAND_ITER
)


def request_cves(keyword, year_range):
    """Send request to `cve.mitre.org` to get html response to parse.

    ## Parameters:
        **keyword** (_str_): keywords to search for related CVE's.
        **year_range** (_str_): REGEX pattern of allowed year frame.

    ### Raises:
        `typer.Exit`: graceful exit in case request goes wrong.

    ### Returns:
        _list_: 
        CVE's parsed from html response.
    """

    # Assemble and send request to cve.mitre.org
    pprint(f"[bright_blue]{PREFIX}Searching by keywords: [bold]{keyword}[/bold]...[/bright_blue]")
    sources = parse_javascript_page(
        CVE_ORG_ENDPOINT,
        param=CVE_ORG_SEARCH_PARAM,
        query=keyword,
        load_element=(By.TAG_NAME, "h2"),
        paginate={
            "action": "next",
            "interact": (By.CLASS_NAME, CVE_ORG_BTN_CLASS)
        }
    )

    # Send html response to parsing function
    cve_list = []
    for response in sources:
        # Find table with CVE in html response
        bs = BeautifulSoup(response, features="html.parser")

        # From all CVE's, retrieve such that match provided year frame.
        # Note: CVE-<year>-<code> is the format of CVE ID's.
        for row in bs.find_all("a"):
            if not row.string:
                continue
            if re.match(rf"\bCVE-({year_range})-\d{{4,6}}\b", row.string):
                cve_list.append(row.string)

    return cve_list

def request_repositories(cve):
    """"""

    sources = parse_javascript_page(
        SEARCH_ENGINE_ENDPOINT,
        param=SEARCH_ENGINE_PARAM,
        query=f"\"{cve}\"",
        load_element=(By.TAG_NAME, "section"),
        dork="site:github.com",
        paginate={
            "action": "expand",
            "interact": (By.ID, SEARCH_ENGINE_BTN_CLASS),
            "iterations": SEARCH_ENGINE_EXPAND_ITER
        }
    )

    if not sources:
        return []

    cve_poc = []
        
    # Retrieve blacklisted keywords to filter
    pattern = get_blacklisted_paterns()

    # Parse Github links
    for page in sources:
        bs = BeautifulSoup(page, features="html.parser")
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
