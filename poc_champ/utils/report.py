"""Module handling job report generation and filename management."""

import os
import re
import json
from rich import print as pprint

from poc_champ.constants import PREFIX

def set_filename(filename, index):
    """Append index to filename gracefully to avoid overwriting.

    ## Parameters:
        **filename** (_str_): Original filename to replace.
        **index** (_int_): Index to append in order for filenames in same directory
        to differ.

    ### Returns:
        _str_: Altered filename with index appended.
    """
    if not re.findall(r"\.", filename):
        return f"{filename}-{str(index)}"

    filename_parts = filename.split(".")
    filename_parts[0] += f"-{str(index)}"
    return ".".join(filename_parts)


def generate_report(filename, result):
    """Cover logic behind checking filename availability, sending it to altering
    and saving data to output filename.

    ## Parameters:
        **filename** (_str_): original filename passed through input.
        **result** (_list_): lists of links to each CVE's POCs.

    ### Returns:
        _str_: final filename to save data to, whether altered or not.
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
