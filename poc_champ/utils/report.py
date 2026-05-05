"""
Module handling job report generation and filename management.

This module provides functions to:
    - Safely generate filenames to avoid overwriting.
    - Save job results to output files.

:func set_filename: Append index to filename to avoid overwriting.
:func generate_report: Save results to a file, altering filename if needed.
"""

import os
import re
import json
from rich import print as pprint

from poc_champ.constants import PREFIX


def set_filename(filename: str, index: int) -> str:
    """
    Append index to filename gracefully to avoid overwriting.

    :param filename str: Original filename to replace.
    :param index int: Index to append in order for filenames in same directory to differ.
    :returns: Altered filename with index appended.
    :rtype: str
    """
    if not re.findall(r"\.", filename):
        return f"{filename}-{str(index)}"

    filename_parts = filename.split(".")
    filename_parts[0] += f"-{str(index)}"
    return ".".join(filename_parts)


def generate_report(filename: str, result: list) -> str:
    """
    Check filename availability, alter if needed, and save data to output filename.

    :param filename str: Original filename passed through input.
    :param result list: List of links to each CVE's PoCs.
    :returns: Final filename to save data to, whether altered or not.
    :rtype: str
    """
    if os.path.exists(f"./output/{filename}"):
        pprint(f"[yellow]{PREFIX}Output file {filename} already exists.[/yellow]")
        i = 1
        while os.path.exists(f"./output/{set_filename(filename, i)}"):
            i += 1
        filename = f"{set_filename(filename, i)}"

    with open(f"output/{filename}", "w", encoding="utf-8") as file:
        file.write(json.dumps(result, indent=2))

    return filename
