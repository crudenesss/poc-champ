"""Repository search service."""

import re

from bs4 import BeautifulSoup

from poc_champ.constants import (
    SEARCH_ENGINE_ENDPOINT,
    SEARCH_ENGINE_PARAM,
    SEARCH_ENGINE_BTN_CLASS,
    SEARCH_ENGINE_EXPAND_ITER,
    SEARCH_ENGINE_EXCLUDE_ENDPOINTS,
)
from poc_champ.scrapers.playwright_scraper import PlaywrightScraper
from poc_champ.scrapers.utils import build_query


def _parse_github_links(pages: list[str]) -> list[str]:
    pattern = "|".join(SEARCH_ENGINE_EXCLUDE_ENDPOINTS)
    links = []
    for html in pages:
        bs = BeautifulSoup(html, features="lxml")
        for link in bs.find_all("a", attrs={"data-testid": "result-title-a"}):
            try:
                href = link["href"]
                if not re.findall(pattern, href) and len(re.findall(r"\/", href)) > 3:
                    links.append(href)
            except KeyError:
                continue
    return links


class RepositorySearcher:  # pylint: disable=too-few-public-methods
    """Searches DuckDuckGo for GitHub POC repositories related to CVEs."""

    def __init__(self, scraper: PlaywrightScraper):
        self._scraper = scraper

    async def search(self, cve_list: list[str], max_workers: int) -> dict[str, list]:
        """Return a mapping of CVE IDs to lists of GitHub repository URLs."""
        urls = [
            build_query(
                SEARCH_ENGINE_ENDPOINT,
                param=SEARCH_ENGINE_PARAM,
                query=f'"{cve}"',
                dork="site:github.com",
            )
            for cve in cve_list
        ]

        all_pages = await self._scraper.fetch_many(
            urls,
            max_workers=max_workers,
            load_selector="ol.react-results--main",
            button_selector=f"button#{SEARCH_ENGINE_BTN_CLASS}",
            iterations=SEARCH_ENGINE_EXPAND_ITER,
        )

        return {
            cve: _parse_github_links(pages)
            for cve, pages in zip(cve_list, all_pages)
        }
