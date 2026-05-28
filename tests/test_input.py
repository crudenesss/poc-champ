"""Tests for the input module."""

import sys
import pytest

from poc_champ.cli import get_parser


class TestInput:

    """Test cases for the ArgParser input handling."""

    def test_success_range_single_year(self, monkeypatch):
        """Provide CVE year range limited to a single year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-r", "2026"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == range(2026, 2027)

    def test_success_range_year_range(self, monkeypatch):
        """Provide CVE year range with a start and end year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-r", "2020-2026"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == range(2020, 2027)

    def test_success_keyword(self, monkeypatch, excpected_default_year_range):
        """Provide minimal valid arguments amount in a form of keyword option.
        
        - Verify the parser returns the time range of last 5 years.
        """
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword"])
        args = get_parser()
        assert args.keyword == "keyword"
        assert args.range == excpected_default_year_range

    def test_fail_invalid_year_range(self, monkeypatch):
        """Provide an invalid year range where the start year is greater than the end year."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-r", "2020/2026"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_fail_none_required_options(self, monkeypatch):
        """Provide none of the required arguments."""
        monkeypatch.setattr(sys, "argv", ["poc-champ"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_fail_unknown_option(self, monkeypatch):
        """Provide an unknown option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-x", "unknown"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_success_cve(self, monkeypatch):
        """Provide valid cve option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "cve", "CVE-2026-0001"])
        args = get_parser()
        assert args.cve_id == "CVE-2026-0001"

    def test_fail_invalid_cve_format(self, monkeypatch):
        """Provide an invalid CVE format."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "cve", "INVALID-CVE-FORMAT"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_fail_conflicting_options(self, monkeypatch):
        """Provide both keyword and CVE option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "cve", "CVE-2026-0001"])
        with pytest.raises(SystemExit):
            get_parser()

    def test_fail_conflicting_subcommand_option(self, monkeypatch):
        """Provide CVE subcommand with range option which is not a part of the cve subcommand."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "cve", "CVE-2026-0001", "-r", "2020-2026"])
        with pytest.raises(SystemExit):
            get_parser()
