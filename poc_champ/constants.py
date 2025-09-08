"""Constants for CVE scraping and search engine configuration.

This module defines all constant values used throughout the application,
including endpoints, parameters, help texts, and decorations.

:var CVE_ORG_ENDPOINT: Endpoint for cve.org search.
:var CVE_ORG_SEARCH_PARAM: Query parameter for cve.org search.
:var CVE_ORG_BTN_CLASS: CSS class for CVE.org pagination button.
:var SEARCH_ENGINE_ENDPOINT: Endpoint for the search engine.
:var SEARCH_ENGINE_PARAM: Query parameter for the search engine.
:var SEARCH_ENGINE_BTN_CLASS: CSS class for search engine expand button.
:var SEARCH_ENGINE_EXPAND_ITER: Number of times to expand search results.
:var SEARCH_ENGINE_EXCLUDE_ENDPOINTS: List of endpoints to exclude from results.
:var YEAR_RANGE_HELP: Help text for year range argument.
:var OUTPUT_HELP: Help text for output argument.
:var PROGRESS_BAR: Progress bar text.
:var PREFIX: Prefix for CLI all info logs in output.
"""

# cve.org scraping data
CVE_ORG_ENDPOINT = "https://www.cve.org/CVERecord/SearchResults"
CVE_ORG_SEARCH_PARAM = "query"
CVE_ORG_BTN_CLASS = "pagination-next button cve-button cve-button-outline"

# Search engine data
SEARCH_ENGINE_ENDPOINT = "https://duckduckgo.com"
SEARCH_ENGINE_PARAM = "q"
SEARCH_ENGINE_BTN_CLASS = "more-results"
SEARCH_ENGINE_EXPAND_ITER = 3

SEARCH_ENGINE_EXCLUDE_ENDPOINTS = [
    "actions",
    "activity",
    "advisories",
    "blob",
    "commit",
    "commits",
    "discussions",
    "docs",
    "gist",
    "issues",
    "labels",
    "milestones",
    "projects",
    "pull",
    "pulls",
    "releases",
    "security",
    "topics",
    "wiki",
    r"\/$",
    r"\?",
]

# Docstrings
YEAR_RANGE_HELP = (
    "Filter CVE by year published.\n"
    "If left empty, return set default range of 5 last years.\n"
    "Allowed formats:\n"
    "    * `<year>`: to set particular year\n"
    "    * `<min_year>-<max_year>`: set year frame"
)
OUTPUT_HELP = "Pass filename to save results into."
PROGRESS_BAR = "[bold bright_blue]Make some tea, while I look for everything...[/bold bright_blue]"

# Decorations
PREFIX = "[*] "
