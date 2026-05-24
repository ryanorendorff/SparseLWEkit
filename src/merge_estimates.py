"""Merge per-parameter partial estimate CSVs into the canonical
src/data/lattice_estimator_estimates.csv.

Used by the refresh-readme CI workflow to combine outputs of the
matrix-sharded estimate jobs back into a single CSV before regenerating
the README. Each partial CSV is the output of:

    sage --python src/estimate_security.py --ids <N> --output partial-<N>.csv

Usage:
    python3 src/merge_estimates.py <glob-pattern> [--output PATH]
"""
import argparse
import glob
import sys

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pattern",
        help="Glob matching all partial CSVs to merge "
        "(e.g. 'partials/estimates-*/partial-*.csv').",
    )
    parser.add_argument(
        "--output",
        default="src/data/lattice_estimator_estimates.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()

    paths = sorted(glob.glob(args.pattern))
    if not paths:
        sys.exit(f"no partial CSVs matched pattern: {args.pattern}")

    merged = (
        pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
        .sort_values("ID")
        .reset_index(drop=True)
    )
    merged.to_csv(args.output, index=False)
    print(merged.to_string(index=False))


if __name__ == "__main__":
    main()
