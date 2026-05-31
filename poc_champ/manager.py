"""Manager module for orchestrating CVE and repository search jobs.

This module provides the main job runner for searching CVEs and related repositories.
"""

import asyncio

from rich import print as pprint
from rich.progress import track

from poc_champ.agents import request_cves, request_repositories
from poc_champ.constants import PROGRESS_BAR, PREFIX
from poc_champ.models import ProcessedArgs


def run_job(args: ProcessedArgs) -> dict:
    """
    Run the main job to search for CVEs and related GitHub repositories.

    :param keyword: Keywords to search for related CVEs.
    :type keyword: str
    :param year_range: Year range argument for filtering CVEs.
    :type year_range: str or None

    :returns: Dictionary mapping CVE IDs to lists of repository URLs.
    :rtype: dict

    :raises RuntimeError: If no CVEs or repositories are found.
    """

    if args.get("keyword"):
        # Get list of CVE's by keyword, raise error if no found
        cve_list = request_cves(args.get("keyword"), args.get("range"))
        if not cve_list:
            raise RuntimeError("No results found. Exiting...")

        pprint(cve_list)
        pprint(f"Found CVE: {len(cve_list)} result(s)\n")
    else:
        cve_list = [args.get("cve_id")]

    # Run async scraping with semaphore-based concurrency
    cve_links = asyncio.run(request_repositories(cve_list, args.get("workers")))
    
    if not cve_links:
        raise RuntimeError(f"\n[bold yellow]{PREFIX}Sorry, no repos were found =([/bold yellow]")

    pprint(f"Found repositories: {cve_links}\n")

    return cve_links
