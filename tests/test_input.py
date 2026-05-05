"""Tests for the input module."""

import sys
import pytest
from unittest.mock import patch

from poc_champ.cli import make_parser


class TestInput:

    """Test cases for the ArgParser input handling."""

    def test_success_keyword(self):
        """Provide minimal valid arguments amount in a form of keyword option."""
        with patch.object(sys, "argv", ["poc-champ", "-k", "keyword"]):
            parser = make_parser()
            args = parser.parse_args()
            assert args.keyword == "keyword"

    def test_success_cve(self):
        """Provide valid cve option."""
        with patch.object(sys, "argv", ["poc-champ", "-c", "CVE-2026-0001"]):
            parser = make_parser()
            args = parser.parse_args()
            assert args.cve == "CVE-2026-0001"

    def test_fail_conflicting_options(self):
        """Provide both keyword and CVE option."""
        with patch.object(sys, "argv", ["poc-champ", "-k", "keyword", "-c", "CVE-2026-0001"]):
            parser = make_parser()
            with pytest.raises(SystemExit):
                parser.parse_args()

    def test_fail_none_required_options(self):
        """Provide none of the required arguments."""
        with patch.object(sys, "argv", ["poc-champ"]):
            parser = make_parser()
            with pytest.raises(SystemExit):
                parser.parse_args()

    def test_success_range_single_year(self):
        """Provide CVE year range limited to a single year."""
        with patch.object(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2026"]):
            parser = make_parser()
            args = parser.parse_args()
            assert args.keyword == "keyword"
            assert args.range == "2026"

    def test_success_range_year_range(self):
        """Provide CVE year range with a start and end year."""
        with patch.object(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2020-2026"]):
            parser = make_parser()
            args = parser.parse_args()
            assert args.keyword == "keyword"
            assert args.range == "2020-2026"

    def test_fail_invalid_range_format(self):
        """Provide an invalid format for the CVE year range."""
        with patch.object(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2020/2026"]):
            parser = make_parser()
            with pytest.raises(SystemExit):
                parser.parse_args()

    def test_fail_invalid_year_range(self):
        """Provide an invalid year range where the start year is greater than the end year."""
        with patch.object(sys, "argv", ["poc-champ", "-k", "keyword", "-r", "2026-2020"]):
            parser = make_parser()
            with pytest.raises(SystemExit):
                parser.parse_args()
