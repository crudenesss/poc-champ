""""""

import typer

from art import text2art
from rich import print as pprint
from rich.progress import track

from poc_champ.utils.parser import parse_year_range
from poc_champ.agents import request_cves, request_repositories
from poc_champ.constants import PROGRESS_BAR, PREFIX

def run_job(keyword, year_range):
    """"""

    # Check validity and retrieve years to filter cve's by
    year_range_pattern = parse_year_range(year_range)

    # Application banner
    pprint(f"[yellow]{text2art('POCChamp', font='fire_font-s')}[/yellow]")

    # Get list of CVE's by keyword, exit if no found
    cve_list = request_cves(keyword, year_range_pattern)
    if not cve_list:
        pprint(f"\n[bold yellow]{PREFIX}No results found =(\n{PREFIX}Exiting...[/bold yellow]")
        raise typer.Exit()

    pprint(
        f"[green]{PREFIX}Found CVE: [/green][bold green]{len(cve_list)} result(s)\n[/bold green]"
    )

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
        pprint(f"\n[bold yellow]{PREFIX}Sorry, no repos were found =([/bold yellow]")
        raise typer.Exit()

    return result
