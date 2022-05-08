import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Enrich EQT website data")
    parser.add_argument("data_dir", help="directory where to store outputs of this program")
    namespace = parser.parse_args()
    return namespace
