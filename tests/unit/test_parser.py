"""Tests for the input module."""

import sys
import pytest

from poc_champ.cli.parser import ConfigParser


@pytest.mark.unit
class TestParser:

    """Test cases for the ArgParser input handling."""

    def test_success_keyword(self, monkeypatch, expected_default_year_range):
        """Provide minimal valid arguments amount in a form of keyword option.
        
        - Verify the parser returns the time range of last 5 years.
        """
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword"])
        parser = ConfigParser("description")
        args = parser.parse()
        assert args.keyword == "keyword"
        assert args.range == expected_default_year_range
        assert args.workers == 1

    def test_fail_none_required_options(self, monkeypatch):
        """Provide none of the required arguments."""
        monkeypatch.setattr(sys, "argv", ["poc-champ"])
        with pytest.raises(SystemExit):
            parser = ConfigParser("description")
            parser.parse()

    def test_fail_unknown_option(self, monkeypatch):
        """Provide an unknown option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "-x", "unknown"])
        with pytest.raises(SystemExit):
            parser = ConfigParser("description")
            parser.parse()

    def test_fail_conflicting_options(self, monkeypatch):
        """Provide both keyword and CVE option."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "key", "keyword", "cve", "CVE-2026-0001"])
        with pytest.raises(SystemExit):
            parser = ConfigParser("description")
            parser.parse()

    def test_fail_conflicting_subcommand_option(self, monkeypatch):
        """Provide CVE subcommand with range option which is not a part of the cve subcommand."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "cve", "CVE-2026-0001", "-r", "2020-2026"])
        with pytest.raises(SystemExit):
            parser = ConfigParser("description")
            parser.parse()

    def test_success_max_workers(self, monkeypatch, expected_default_year_range):
        """Provide keyword option and adjust maximum workers number."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "-w", "4", "key", "keyword"])
        parser = ConfigParser("description")
        args = parser.parse()
        assert args.keyword == "keyword"
        assert args.range == expected_default_year_range
        assert args.workers == 4

    def test_fail_invalid_max_workers(self, monkeypatch):
        """Provide maximum workers value in wrong format."""
        monkeypatch.setattr(sys, "argv", ["poc-champ", "-w", "invalid", "key", "keyword"])
        with pytest.raises(SystemExit):
            parser = ConfigParser("description")
            parser.parse()
