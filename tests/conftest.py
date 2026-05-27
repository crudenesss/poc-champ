"""This module contains pytest shared configs and misc setup."""

import pytest

from datetime import datetime


@pytest.fixture
def excpected_default_year_range():
    """Fixture to provide the expected default year range for tests."""
    current_year = datetime.now().year
    return [str(current_year - 4), str(current_year)]
