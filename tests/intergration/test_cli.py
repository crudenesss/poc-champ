"""Integration tests for the cli system."""

import sys
import pytest

from poc_champ.cli import get_parser


class TestInput:

    """Test cases for the unified cli input handling."""

    def test_cli_success_range_single_year(self, monkeypatch):
        """Provide CVE year range limited to a single year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-r", "2026"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == "2026"

    def test_cli_success_range_year_range(self, monkeypatch):
        """Provide CVE year range with a start and end year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-r", "2020-2026"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == "2020|2021|2022|2023|2024|2025|2026"

    def test_cli_fail_invalid_year_range(self, monkeypatch):
        """Provide an invalid year range where the start year is greater than the end year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-r", "2020/2026"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_cli_success_cve(self, monkeypatch):
        """Provide valid cve option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "cve", "CVE-2026-0001"])
        args = get_parser()
        assert args.cve_id == "CVE-2026-0001"

    def test_cli_fail_invalid_cve_format(self, monkeypatch):
        """Provide an invalid CVE format."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "cve", "INVALID-CVE-FORMAT"])
        with pytest.raises(SystemExit):
            get_parser()
