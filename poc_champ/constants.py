"""Constants necessary"""

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
