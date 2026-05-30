"""Module with parser factory."""

from poc_champ.cli.parser import ConfigParser

def get_parser():
    """Factory function to get the CLI argument parser instance."""
    parser = ConfigParser(
        "Web-scraping CLI tool to retrieve links to Github repositories"
        "containing POC (Proof of Concept) to CVEs.")
    return parser.parse()
