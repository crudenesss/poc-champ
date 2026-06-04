"""CVE fetching service."""

import re

from bs4 import BeautifulSoup
from rich import print as pprint

from poc_champ.constants import (
    PREFIX,
    CVE_ORG_ENDPOINT,
    CVE_ORG_BTN_CLASS,
    CVE_ORG_SEARCH_PARAM,
)
from poc_champ.scrapers.playwright_scraper import PlaywrightScraper
from poc_champ.scrapers.utils import build_query


def _parse_cve_ids(html: str, year_range: str) -> list[str]:
    bs = BeautifulSoup(html, features="lxml")
    results = []
    for row in bs.find_all("a"):
        if not row.string:
            continue
        if re.match(rf"\bCVE-({year_range})-\d{{4,}}\b", row.string):
            results.append(row.string)
    return results


class CVEFetcher:  # pylint: disable=too-few-public-methods
    """Fetches CVE identifiers from cve.org by keyword and year range."""

    def __init__(self, scraper: PlaywrightScraper):
        self._scraper = scraper

    async def fetch(self, keyword: str, year_range: str) -> list[str]:
        """Search cve.org for CVEs matching keyword, filtered by year range."""
        pprint(
            f"[bright_blue]{PREFIX}Searching by keywords: "
            f"[bold]{keyword}[/bold]...[/bright_blue]"
        )

        url = build_query(CVE_ORG_ENDPOINT, param=CVE_ORG_SEARCH_PARAM, query=keyword)
        cve_list = []

        async for html in self._scraper.stream_pages(
            url,
            load_selector="h2",
            button_selector=f"button.{CVE_ORG_BTN_CLASS}",
        ):
            matches = _parse_cve_ids(html, year_range)
            if not matches:
                break
            cve_list.extend(matches)

        return cve_list
