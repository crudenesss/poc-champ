"""Core data models for the PoC Champ application."""

from typing import Optional, TypedDict


class ProcessedArgs(TypedDict):
    keyword: Optional[str]
    cve_id: Optional[str]
    range: Optional[str]
    workers: int
