import asyncio
import json

from art import text2art
from rich import print as pprint

from poc_champ.cli import get_parser
from poc_champ.constants import PREFIX
from poc_champ.core.manager import JobManager
from poc_champ.scrapers import PlaywrightScraper
from poc_champ.services.cve.fetcher import CVEFetcher
from poc_champ.services.repository.searcher import RepositorySearcher


def app():
    pprint(f"[yellow]{text2art('POCChamp', font='fire_font-s')}[/yellow]")

    args = vars(get_parser())
    scraper = PlaywrightScraper()
    manager = JobManager(
        cve_fetcher=CVEFetcher(scraper),
        repo_searcher=RepositorySearcher(scraper),
    )

    try:
        result = asyncio.run(manager.run(args))
        pprint(json.dumps(result))
    except RuntimeError as err:
        pprint(f"{PREFIX}{err}")
