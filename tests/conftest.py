"""This module contains pytest shared configs and misc setup."""

import pytest

from datetime import datetime

DEFAULT_YEAR_COUNT = 5

@pytest.fixture
def expected_default_year_range():
    """Fixture to provide the expected default year range for tests."""
    upper_year_threshold = datetime.now().year + 1
    year_range = range(upper_year_threshold - DEFAULT_YEAR_COUNT, upper_year_threshold)
    return "|".join([str(year) for year in year_range])
