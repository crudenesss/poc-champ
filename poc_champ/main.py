"""Main module for the poc-champ CLI tool.

This module defines the entry point for the command-line interface,
allowing users to search for CVEs and related GitHub repositories and
generate reports.
"""

import json
from art import text2art
from rich import print as pprint

from poc_champ.manager import run_job
from poc_champ.constants import PREFIX
from poc_champ.cli import get_parser


def app():
    """
    Web-scraping CLI tool to retrieve links to Github repositories containing
    POC (Proof of Concept) to CVE's of interest.
    """

    # Application banner
    pprint(f"[yellow]{text2art('POCChamp', font='fire_font-s')}[/yellow]")

    args = vars(get_parser())
    try:
        result = run_job(args)
        pprint(json.dumps(result))
    except RuntimeError as err:
        pprint(f"{PREFIX}{err}")
