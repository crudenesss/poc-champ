"""Main module"""

import json
from typing import Optional
from typing_extensions import Annotated
from art import text2art
import typer
from rich import print as rich_print
from rich.progress import track

from poc_champ.helpers import request_cves, request_from_duckduckgo, output_file, parse_year_range
from poc_champ.constants import YEAR_RANGE_HELP, OUTPUT_HELP, PROGRESS_BAR, PREFIX

app = typer.Typer(name="poc-champ", add_completion=False)


@app.command()
def main(
    keyword: Annotated[
        str,
        typer.Option(
            "-k",
            "--keyword",
            help="Keywords to find related CVE's by.",
            show_default=False,
        ),
    ],
    year_range: Annotated[
        Optional[str],
        typer.Option("-r", "--range", help=YEAR_RANGE_HELP, show_default=False),
    ] = None,
    output: Annotated[
        Optional[str],
        typer.Option("-o", "--output", help=OUTPUT_HELP, show_default=False),
    ] = None,
    secret: Annotated[bool, typer.Option("--secret", help="Trust me.")] = False,
):

    """Web-scrapping CLI tool to retrieve links to Github repositories containing
    POC (Proof of Concept) to CVE's of interest.
    """

    # Check validity and retrieve years to filter cve's by
    year_range_pattern = parse_year_range(year_range)

    # Application banner
    rich_print(f"[yellow]{text2art('POCChamp', font='fire_font-s')}[/yellow]")

    # Get list of CVE's by keyword, exit if no found
    cve_list = request_cves(keyword, year_range_pattern)
    if not cve_list:
        rich_print(f"\n[bold yellow]{PREFIX}No results found =(\n{PREFIX}Exiting...[/bold yellow]")
        raise typer.Exit()

    rich_print(
        f"[green]{PREFIX}Found CVE: [/green][bold green]{len(cve_list)} result(s)\n[/bold green]"
    )

    result = []

    for cve in track(
        cve_list,
        description=PROGRESS_BAR,
        transient=True,
    ):

        cve_links = request_from_duckduckgo(cve)
        if cve_links:
            cve_result = {cve: cve_links}
            result.append(cve_result)

    if not result:
        rich_print(f"\n[bold yellow]{PREFIX}Sorry, no repos were found =([/bold yellow]")
        raise typer.Exit()

    if not output:
        rich_print(json.dumps(result, indent=2))
    else:
        output = output_file(output, result)
        rich_print(f"[bold bright_blue]{PREFIX}Saved to {output}.[/bold bright_blue]")

    if secret:
        rich_print("Temp")
