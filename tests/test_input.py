"""Tests for the input module."""

import sys
import pytest

from poc_champ.cli import get_parser


class TestInput:

    """Test cases for the ArgParser input handling."""

    def test_success_range_single_year(self, monkeypatch):
        """Provide CVE year range limited to a single year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2026"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == "2026"

    def test_success_range_year_range(self, monkeypatch):
        """Provide CVE year range with a start and end year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2020-2026"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == ["2020", "2026"]

    def test_fail_invalid_year_range(self, monkeypatch):
        """Provide an invalid year range where the start year is greater than the end year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2020/2026"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_fail_none_required_options(self, monkeypatch):
        """Provide none of the required arguments."""
        monkeypatch.setattr(sys, "argv", ["poc-champ"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_fail_unknown_option(self, monkeypatch):
        """Provide an unknown option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "-k", "keyword", "-x", "unknown"])
        with pytest.raises(SystemExit):
            get_parser()
