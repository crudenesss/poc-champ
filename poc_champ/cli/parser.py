"""Module for CLI argument parsing and validation."""

import argparse

from datetime import datetime

from poc_champ.cli.validators import YearRangeValidator, CveValidator


class ConfigParser:

    """Parser instance with argument initialisation and processing."""

    DEFAULT_YEAR_GAP = 4

    def __init__(self, description):
        self.parser = argparse.ArgumentParser(description=description)
        self._setup_arguments()

    def _setup_arguments(self):
        """Initialise CLI arguments."""
        self.parser.add_argument(
            "-w", "--max-workers",
            type=int,
            dest="workers",
            help="Set the maximum number of workers used in webcrawling job.",
            default=1
        )
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
            type=YearRangeValidator(),
            default=self._set_default_year_range()
        )

        parser_cve = subparsers.add_parser(
            "cve",
            help="Search CVE's POCs by already provided CVE ID."
        )
        parser_cve.add_argument(
            "cve_id",
            type=CveValidator(),
            help="CVE ID to find related POCs for."
        )

    def _set_default_year_range(self):
        upper_year = datetime.now().year
        year_list = [upper_year - self.DEFAULT_YEAR_GAP, upper_year]
        return "-".join([str(year) for year in year_list])

    def parse(self) -> argparse.Namespace:
        """Wrapper method around argparse internal processing. 
        
        Returns parsed values as an object.
        """
        return self.parser.parse_args()
