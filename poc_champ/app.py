"""Main module"""

import re
import os
from typing import Optional
from typing_extensions import Annotated
import requests
import typer
from rich import print as rich_print

from poc_parser import parse_response, parse_year_range
from constants import CVE_MITRE_LINK, SEARCH_REPOSITORIES_ENDPOINT

app = typer.Typer(name="poc-champ", add_completion=False)


@app.command()
def main(
    keyword: Annotated[str, typer.Argument()],
    auth_token: Annotated[str, typer.Option("-t", "--token")] = None,
    year_range: Annotated[Optional[str], typer.Option("-r", "--range")] = None,
    secret: Annotated[bool, typer.Option("--secret")] = False,
):

    # Retrieve token, if not found, close the app
    if not auth_token:
        if os.getenv("AUTH_TOKEN"):
            auth_token = os.getenv("AUTH_TOKEN")
        else:
            rich_print("""[bold red]No API token provided.[/bold red]
Use [bold bright_blue]--help[/bold bright_blue] for getting more information.""")
            raise typer.Exit()

    # Retrieve years to filter cve's by
    year_range_pattern = parse_year_range(year_range)

    rich_print(f"Searching by keywords: {keyword}...")
    keywords_prepared = re.sub(" ", "+", keyword, count=-1)
    response = requests.get(
        CVE_MITRE_LINK,
        params={"keyword": keywords_prepared},
        timeout=10,
    )
    if response.status_code != 200:
        rich_print(
            """Oops! Something went wrong =(
            Try checking internet connection"""
        )
        raise typer.Exit()

    cve_list = parse_response(response.text, year_range_pattern)
    rich_print("Found CVE:")
    rich_print(cve_list)

    result = []

    # Make request via Github API
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {auth_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    for cve in cve_list:
        response = requests.get(
            SEARCH_REPOSITORIES_ENDPOINT,
            params={"q": cve},
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            rich_print(
                "Oops! Something went wrong =(\nCheck your authentication token"
            )
            raise typer.Exit()

        cve_result = {
            cve: [
                item.get("html_url") for item in response.json().get("items")
            ]
        }

        result.append(cve_result)

    rich_print(result)

    if secret:
        rich_print("\n[bold bright_blue]P.S.: I love you :heart:[/bold bright_blue]")


if __name__ == "__main__":
    app()
