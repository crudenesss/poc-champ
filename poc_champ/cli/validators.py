"""Semantic and logical input validators."""

import re


class BaseValidator():

    """Base class with common validators."""

    def _is_valid_format(self, value: str, pattern: str):
        regex = re.compile(pattern)
        return re.match(regex, value)


class YearRangeValidator(BaseValidator):

    """Class for validating and processing year range input."""

    YEAR_RANGE_REGEX = r"(^\d{4}$)|(^\d{4}-\d{4}$)"

    def __call__(self, value: str):
        if not self._is_valid_format(value, self.YEAR_RANGE_REGEX):
            raise ValueError(f"Argument {value} is not a valid range.")

        return self._process_year_range(value)

    def _process_year_range(self, value: str) -> range:
        year_range = value.split("-")
        if len(year_range) == 1:
            result = range(int(year_range[0]), int(year_range[0]) + 1)
        else:
            result = range(int(year_range[0]), int(year_range[1]) + 1)
        return result


class CveValidator(BaseValidator):

    """Class for validating CVE ID format."""

    CVE_REGEX = r"^CVE-\d{4}-\d{4,}$"

    def __call__(self, value: str):
        if not self._is_valid_format(value, self.CVE_REGEX):
            raise ValueError(f"Argument {value} is not a valid CVE format.")

        return value
