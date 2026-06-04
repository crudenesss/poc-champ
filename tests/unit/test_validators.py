"""Tests for validators."""

import pytest

from poc_champ.cli.validators import CveValidator, YearRangeValidator


@pytest.mark.unit
class TestCveValidator:

    """Test cases for CVE ID validation."""

    def test_fail_invalid_cve_format(self):
        """Provide an invalid CVE format."""
        cve = "INVALID-CVE-FORMAT"
        validate = CveValidator()
        with pytest.raises(ValueError):
            validate(cve)

    def test_success_valid_cve(self):
        """Provide valid CVE ID"""
        cve = "CVE-2026-0001"
        validate = CveValidator()
        assert cve == validate(cve)


@pytest.mark.unit
class TestYearValidator:

    """Test cases for year range validation."""

    def test_success_valid_single_year(self):
        """Provide valid single year."""

        year = "2026"
        validate = YearRangeValidator()
        assert validate(year) == "2026"

    def test_success_valid_year_range(self):
        """Provide valid year range."""

        year_range = "2020-2026"
        validate = YearRangeValidator()
        assert validate(year_range) == "2020|2021|2022|2023|2024|2025|2026"

    def test_fail_invalid_year_range_format(self):
        """Provide year range with invalid syntax."""

        year_range = "2020/2026"
        validate = YearRangeValidator()
        with pytest.raises(ValueError):
            validate(year_range)
