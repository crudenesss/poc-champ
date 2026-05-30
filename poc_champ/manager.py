"""Manager module for orchestrating CVE and repository search jobs.

This module provides the main job runner for searching CVEs and related repositories.
"""

from rich import print as pprint
from rich.progress import track

from poc_champ.agents import request_cves, request_repositories
from poc_champ.constants import PROGRESS_BAR, PREFIX
from poc_champ.models import ProcessedArgs


def run_job(args: ProcessedArgs) -> list[dict[str, list]]:
    """
    Run the main job to search for CVEs and related GitHub repositories.

    :param keyword: Keywords to search for related CVEs.
    :type keyword: str
    :param year_range: Year range argument for filtering CVEs.
    :type year_range: str or None

    :returns: List of dictionaries mapping CVE IDs to lists of repository URLs.
    :rtype: list

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

    result = []

    for cve in track(
        cve_list,
        description=PROGRESS_BAR,
        transient=True,
    ):
        cve_links = request_repositories(cve)
        if cve_links:
            cve_result = {cve: cve_links}
            result.append(cve_result)

    if not result:
        raise RuntimeError(f"\n[bold yellow]{PREFIX}Sorry, no repos were found =([/bold yellow]")

    return result
