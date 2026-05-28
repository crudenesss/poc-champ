"""Module for CLI argument parsing and validation."""

import argparse
import re
import sys

from datetime import datetime


class ConfigParser:

    """Parser instance with argument initialisation and processing."""

    def __init__(self, description):
        self.parser = argparse.ArgumentParser(description=description)
        self._setup_arguments()

    def _setup_arguments(self):
        """Initialise CLI arguments."""
        subparsers = self.parser.add_subparsers(required=True)

        parser_key = subparsers.add_parser(
            "key", 
            help="Search CVE's POCs by keywords mentioned in CVE description."
        )
        parser_key.add_argument(
            "keyword",
            type=str,
            help="Keywords to find related CVE's by."
        )
        parser_key.add_argument(
            "-r", "--range", 
            type=self._validate_year_range,
            default=self._set_default_year_range()
        )

        parser_cve = subparsers.add_parser(
            "cve",
            help="Search CVE's POCs by already provided CVE ID."
        )
        parser_cve.add_argument(
            "cve_id",
            type=self._validate_cve_format,
            help="CVE ID to find related POCs for."
        )

    @staticmethod
    def _set_default_year_range():
        upper_year_threshold = datetime.now().year + 1
        return range(upper_year_threshold - 5, upper_year_threshold)

    @staticmethod
    def _validate_year_range(year_range):
        if re.match(r"(^\d{4}$)|(^\d{4}-\d{4}$)", year_range):
            year_range = year_range.split("-")
        else:
            print(f"Argument {year_range} is not a valid range.")
            sys.exit(1)

        if len(year_range) == 1:
            result = range(int(year_range[0]), int(year_range[0]) + 1)
        else:
            result = range(int(year_range[0]), int(year_range[1]) + 1)

        return result

    @staticmethod
    def _validate_cve_format(cve):
        if not re.match(r"^CVE-\d{4}-\d{4,}$", cve):
            print(f"Argument {cve} is not a valid CVE format.")
            sys.exit(1)
        return cve

    def parse(self) -> argparse.Namespace:
        """Wrapper method around argparse internal processing. 
        
        Returns parsed values as an object.
        """
        return self.parser.parse_args()
