"""
Agents module for CVE and repository search.

This module provides functions to request CVE identifiers from cve.org
and to search for related GitHub repositories using a search engine.

Functions:
    - request_cves: Search for CVEs by keyword and year range (synchronous).
    - request_repositories: Search for GitHub repositories related to CVEs (asynchronous).
"""

import re
import asyncio

from typing import Any

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from rich import print as pprint

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
    Send request to `cve.org` to get HTML response to parse (synchronous using Playwright).

    :param keyword: Keywords to search for related CVEs.
    :type keyword: str
    :param year_range: Regex pattern of allowed year frame.
    :type year_range: str

    :returns: List of CVEs parsed from HTML response.
    :rtype: list
    """
    # Assemble and send request to cve.org
    pprint(
        f"[bright_blue]{PREFIX}Searching by keywords: [bold]{keyword}[/bold]...[/bright_blue]"
    )

    # Run async Playwright code synchronously
    sources = asyncio.run(_fetch_cve_pages(keyword))

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


async def _fetch_cve_pages(keyword: str) -> list[str]:
    """
    Fetch CVE pages from cve.org using Playwright (async helper).

    :param keyword: Keywords to search for related CVEs.
    :type keyword: str

    :returns: List of page sources.
    :rtype: list[str]
    """
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Build query URL
            query_url = build_query(
                CVE_ORG_ENDPOINT,
                param=CVE_ORG_SEARCH_PARAM,
                query=keyword,
            )

            # Navigate to page
            await page.goto(query_url, wait_until="networkidle", timeout=30000)

            # Paginate through results
            pages = await async_paginate(
                page,
                load_selector="h2",
                button_selector=f"button.{CVE_ORG_BTN_CLASS}",
                action="next"
            )

            pprint(f"\n[bright_blue]{PREFIX}Found CVE: {len(pages)} page(s) with results.[/bright_blue]\n")
            return pages

        except Exception as e:
            pprint(f"[yellow]Error fetching CVE pages: {str(e)}[/yellow]")
            return []

        finally:
            await context.close()
            await browser.close()


def build_query(endpoint: str, param: str, query: str, **kwargs: Any) -> str:
    """Build query string for search engine request.

    :param endpoint: Search engine endpoint URL.
    :param param: Query parameter name.
    :param query: Search query string.
    :param kwargs: Additional parameters for dork.

    :returns: Full query string for search engine request.
    """
    dork = kwargs.get("dork", "")
    request = f'{endpoint}?{param}={query} {dork}'
    return request.strip()


async def async_paginate(
    page,
    load_selector: str,
    button_selector: str,
    action: str,
    iterations: int = 1,
) -> list[str]:
    """
    Paginate through pages using Playwright by interacting with buttons.

    :param page: Playwright page instance.
    :param load_selector: CSS selector for element to wait for.
    :param button_selector: CSS selector for pagination button.
    :param action: Action to perform ("next" or "expand").
    :param iterations: Number of pagination iterations.

    :returns: List of page sources collected during pagination.
    """
    pages = []
    counter = 0

    while counter < iterations:
        try:
            # Wait for button to be visible and enabled, then click it
            button_locator = page.locator(button_selector).first
            await button_locator.wait_for(state="visible", timeout=10000)
            await button_locator.click()
            
            # Wait for new content to load
            load_locator = page.locator(load_selector)
            await load_locator.wait_for(state="visible", timeout=10000)
            
            if action == "next":
                pages.append(await page.content())
            
            if iterations > 1:
                counter += 1
        except PlaywrightTimeoutError:
            # If button is not found or content does not load, assume no more pages
            pages.append(await page.content())
            break

    if action == "expand":
        pages.append(await page.content())

    return pages


async def async_scrape_cve(
    browser,
    semaphore: asyncio.Semaphore,
    cve: str,
) -> dict[str, list]:
    """
    Scrape GitHub repositories for a single CVE using Playwright.

    :param browser: Playwright browser instance.
    :param semaphore: Asyncio semaphore to limit concurrency.
    :param cve: CVE identifier to search for.

    :returns: Dictionary mapping CVE to list of repository URLs.
    """
    async with semaphore:
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Build query URL
            query_url = build_query(
                SEARCH_ENGINE_ENDPOINT,
                param=SEARCH_ENGINE_PARAM,
                query=f'"{cve}"',
                dork="site:github.com",
            )

            # Navigate to page
            await page.goto(query_url, wait_until="networkidle", timeout=30000)

            # Paginate through results
            pages = await async_paginate(
                page,
                load_selector="ol.react-results--main",
                button_selector=f"button#{SEARCH_ENGINE_BTN_CLASS}",
                action="expand",
                iterations=SEARCH_ENGINE_EXPAND_ITER,
            )

            if not pages:
                return {cve: []}

            # Parse GitHub links from all pages
            def get_blacklisted_patterns() -> str:
                return "|".join(SEARCH_ENGINE_EXCLUDE_ENDPOINTS)

            pattern = get_blacklisted_patterns()
            link_result = []

            for page_html in pages:
                bs = BeautifulSoup(page_html, features="lxml")
                links = bs.find_all("a", attrs={"data-testid": "result-title-a"})

                for link in links:
                    try:
                        href = link["href"]
                        # Add to result only if it is a clean repository link
                        if (
                            not re.findall(pattern, href)
                            and len(re.findall(r"\/", href)) > 3
                        ):
                            link_result.append(href)
                    except KeyError:
                        continue

            return {cve: link_result}

        except Exception as e:
            pprint(f"[yellow]Error scraping {cve}: {str(e)}[/yellow]")
            return {cve: []}
        
        finally:
            await context.close()


async def request_repositories(cve_list: list, max_workers: int) -> dict:
    """
    Search for GitHub repositories related to given CVEs using async Playwright.

    :param cve_list: List of CVE identifiers to search for.
    :param max_workers: Maximum number of concurrent browser instances.

    :returns: Dictionary mapping CVE IDs to lists of repository URLs.
    """
    semaphore = asyncio.Semaphore(max_workers)
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        
        # Create tasks for all CVEs
        tasks = [
            async_scrape_cve(browser, semaphore, cve)
            for cve in cve_list
        ]
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        await browser.close()
    
    # Merge results into single dictionary
    cve_poc = {}
    for result in results:
        if isinstance(result, dict):
            cve_poc.update(result)
    
    return cve_poc
