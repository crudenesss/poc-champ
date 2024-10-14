"""Constants necessary"""

# Links
CVE_MITRE_LINK = "https://cve.mitre.org/cgi-bin/cvekey.cgi"
SEARCH_DUCKDUCKGO_ENDPOINT = "https://duckduckgo.com"

# Docstrings
YEAR_RANGE_HELP = """Filter CVE by year published.
    If left empty, return set default range of 5 last years.       
    Allowed formats:\n
        * `<year>`: to set particular year\n
        * `<min_year>-<max_year>`: set year frame
"""
OUTPUT_HELP = "Pass filename to save results into."
PROGRESS_BAR = "[bold bright_blue]Make some tea, while I look for everything :tea:[/bold bright_blue]"
