"""Playwright-based scraper with pagination and concurrency support."""

import asyncio
from collections.abc import AsyncGenerator

from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)
from rich import print as pprint


class PlaywrightScraper:
    
    """Playwright-based scraper with pagination and concurrency support."""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self._headless = headless
        self._timeout = timeout

    async def _expand(
        self,
        page: Page,
        load_selector: str,
        button_selector: str,
        iterations: int,
    ) -> list[str]:
        for _ in range(iterations):
            try:
                button = page.locator(button_selector).first
                await button.wait_for(state="visible", timeout=10000)
                await button.click()
                await page.locator(load_selector).wait_for(state="visible", timeout=10000)
            except PlaywrightTimeoutError:
                break
        return [await page.content()]

    async def stream_pages(
        self,
        url: str,
        load_selector: str,
        button_selector: str,
    ) -> AsyncGenerator[str, None]:
        """Yield page HTML sources one at a time as next-page pagination proceeds.

        The consumer controls termination — break out of the async for to stop early.
        Browser cleanup is guaranteed via the finally block on generator close.
        """
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self._headless)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=self._timeout)
                yield await page.content()

                while True:
                    try:
                        button = page.locator(button_selector).first
                        await button.wait_for(state="visible", timeout=10000)
                        await button.click()
                        await page.locator(load_selector).wait_for(state="visible", timeout=10000)
                        yield await page.content()
                    except PlaywrightTimeoutError:
                        break
            except Exception as e:
                pprint(f"[yellow]Error streaming {url}: {e}[/yellow]")
            finally:
                await context.close()
                await browser.close()

    async def _fetch_with_context(
        self,
        browser: Browser,
        semaphore: asyncio.Semaphore,
        url: str,
        load_selector: str,
        button_selector: str,
        iterations: int,
    ) -> list[str]:
        async with semaphore:
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=self._timeout)
                return await self._expand(page, load_selector, button_selector, iterations)
            except Exception as e:
                pprint(f"[yellow]Error scraping {url}: {e}[/yellow]")
                return []
            finally:
                await context.close()

    async def fetch_many(
        self,
        urls: list[str],
        max_workers: int,
        load_selector: str,
        button_selector: str,
        iterations: int = 1,
    ) -> list[list[str]]:
        """Scrape multiple URLs concurrently using a shared browser and semaphore.

        Returns a list aligned with `urls` — each element is the page sources for that URL.
        """
        semaphore = asyncio.Semaphore(max_workers)

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self._headless)

            tasks = [
                self._fetch_with_context(
                    browser, semaphore, url, load_selector, button_selector, iterations
                )
                for url in urls
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            await browser.close()

        return [r if isinstance(r, list) else [] for r in results]
