"""Main module"""

import json
from typing import Optional
from typing_extensions import Annotated
from art import text2art
import typer
from rich import print as rich_print
from rich.progress import track

from poc_champ.poc_parser import (
    request_cves,
    request_from_duckduckgo,
)

app = typer.Typer(name="poc-champ", add_completion=False)


@app.command()
def main(
    keyword: Annotated[str, typer.Option("-k", "--keyword")],
    year_range: Annotated[Optional[str], typer.Option("-r", "--range")] = None,
    secret: Annotated[bool, typer.Option("--secret")] = False,
):
    rich_print(f"[bold yellow]{text2art('POCchamp', font='fire_font-s')}[/bold yellow]")

    # Get list of CVE's by keyword, exit if no found
    cve_list = request_cves(keyword, year_range)
    if not cve_list:
        rich_print("[bold yellow]No results found =(\nExiting...[/bold yellow]")
        raise typer.Exit()

    rich_print(f"[green]Found CVE: [/green][bold green]{len(cve_list)} result(s)[/bold green]")

    result = []

    for cve in track(
        cve_list,
        description="[bold bright_blue]Make some tea, while I look for everything :tea:[/bold bright_blue]",
        transient=True,
    ):

        cve_links = request_from_duckduckgo(cve)
        if cve_links:
            cve_result = {cve: cve_links}
            result.append(cve_result)

    if not result:
        rich_print("[bold yellow]Sorry, no repos were found =([/bold yellow]")
    else:
        rich_print(json.dumps(result, indent=2))

    if secret:
        rich_print("\n[bold bright_blue]P.S.: I love you :heart:[/bold bright_blue]")
