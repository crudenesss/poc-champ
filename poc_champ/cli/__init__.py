import argparse

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", type=str)
    parser.add_argument("-r", "--range", type=str)
    return parser.parse_args()
