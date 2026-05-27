import argparse
import re
import sys

from datetime import datetime

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", type=str, required=True)
    parser.add_argument("-r", "--range", type=str)
    args = parser.parse_args()
    if not args.range:
        upper_year_threshold = datetime.now().year
        args.range = [str(upper_year_threshold - 4), str(upper_year_threshold)]
    elif re.match(r"^\d{4}-\d{4}$", args.range):
        args.range = args.range.split("-")
    elif re.match(r"^\d{4}$", args.range):
        pass
    else:
        print(f"Argument {args.range} is not a valid range.")
        sys.exit(1)
    return args
