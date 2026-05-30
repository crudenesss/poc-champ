"""Module which contains application specific models."""

from typing import Optional, TypedDict


class ProcessedArgs(TypedDict):

    """Processed arguments extracted from the CLI."""

    keyword: Optional[str]
    cve_id: Optional[str]
    range: Optional[str]
    workers: int
