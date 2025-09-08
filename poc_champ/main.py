"""Main module"""

import json
from typing import Optional
from typing_extensions import Annotated
import typer
from rich import print as pprint

from poc_champ.utils.report import generate_report
from poc_champ.manager import run_job
from poc_champ.constants import YEAR_RANGE_HELP, OUTPUT_HELP, PREFIX

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

    result = run_job(keyword, year_range)

    if not output:
        pprint(json.dumps(result, indent=2))
    else:
        output = generate_report(output, result)
        pprint(f"[bold bright_blue]{PREFIX}Saved to {output}.[/bold bright_blue]")

    if secret:
        pprint("Temp")
