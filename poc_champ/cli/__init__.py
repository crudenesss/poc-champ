import argparse
import re

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", type=str)
    parser.add_argument("-r", "--range", type=str)
    args = parser.parse_args()
    if re.match(r"^\d{4}-\d{4}$", args.range):
        args.range = args.range.split("-")
    elif re.match(r"^\d{4}$", args.range):
        pass
    else:
        exit(1)
    return args
