"""Wrapper for managing the overall workflow of fetching CVEs and searching repositories."""

from rich import print as pprint

from poc_champ.constants import PREFIX
from poc_champ.core.models import ProcessedArgs
from poc_champ.services.cve.fetcher import CVEFetcher
from poc_champ.services.repository.searcher import RepositorySearcher


class JobManager:

    """Main orchestrator for running CVE and repository search jobs."""

    def __init__(self, cve_fetcher: CVEFetcher, repo_searcher: RepositorySearcher):
        self._cve_fetcher = cve_fetcher
        self._repo_searcher = repo_searcher

    async def run(self, args: ProcessedArgs) -> dict:
        """Run the main job to search for CVEs and related GitHub repositories."""
        if args.get("keyword"):
            cve_list = await self._cve_fetcher.fetch(args["keyword"], args["range"])
            if not cve_list:
                raise RuntimeError("No results found. Exiting...")
            pprint(cve_list)
            pprint(f"Found CVE: {len(cve_list)} result(s)\n")
        else:
            cve_list = [args["cve_id"]]

        cve_links = await self._repo_searcher.search(cve_list, args["workers"])

        if not cve_links:
            raise RuntimeError(f"\n[bold yellow]{PREFIX}Sorry, no repos were found =([/bold yellow]")

        pprint(f"Found repositories: {cve_links}\n")
        return cve_links
