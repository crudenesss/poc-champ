"""
Main entry point for the poc-champ CLI tool.

This module invokes the Typer application for the command-line interface.

:raises Exception: Propagates any exception from the CLI app.
"""

from poc_champ.main import app

app(prog_name="poc-champ")
