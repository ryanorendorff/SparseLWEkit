"""Merge per-parameter partial estimate CSVs into the canonical
src/data/lattice_estimator_estimates.csv.

Used by the refresh-readme CI workflow to combine outputs of the
matrix-sharded estimate jobs back into a single CSV before regenerating
the README. Each partial CSV is the output of:

    sage --python src/estimate_security.py --ids <N> --output partial-<N>.csv

Usage:
    python3 src/merge_estimates.py <glob-pattern> \\
        --parameter-db src/data/parameter_db.csv \\
        [--output PATH]

When --parameter-db is supplied the merged CSV is validated against it:
every row's ID must appear in the parameter database, the ID set must
match exactly, and every attack-cost cell must parse as a finite float
or `inf`. The estimator output is the source of published security
claims so it is checked rather than trusted.
"""
import argparse
import glob
import math
import sys

import pandas as pd

# Attack columns the lattice estimator emits. Order/membership comes from
# estimate_security.py and may grow over time; new columns will simply
# pass through unchecked, but the columns we know about are validated.
KNOWN_ATTACK_COLUMNS = (
    "usvp",
    "bdd",
    "bdd_hybrid",
    "bdd_mitm_hybrid",
    "dual",
    "dual_hybrid",
)

METADATA_COLUMNS = (
    "ID",
    r"$\log_2(n)$",
    r"σ",
    r"$\log_2(q)$",
    r"$h$",
    "estimation_time",
    "machine_info",
    "tool_commit",
)


def _validate(merged: pd.DataFrame, parameter_db_path: str) -> None:
    expected = pd.read_csv(parameter_db_path)
    expected_ids = sorted(int(x) for x in expected["ID"].tolist())
    got_ids = sorted(int(x) for x in merged["ID"].tolist())
    if got_ids != expected_ids:
        sys.exit(
            f"merged ID set {got_ids} does not match parameter_db {expected_ids}"
        )

    # Every attack-cost cell must be a float (finite or inf), not text.
    for col in KNOWN_ATTACK_COLUMNS:
        if col not in merged.columns:
            continue
        for idx, value in enumerate(merged[col]):
            try:
                f = float(value)
            except (TypeError, ValueError):
                sys.exit(f"row {idx} column {col!r}: {value!r} is not a number")
            if math.isnan(f):
                sys.exit(f"row {idx} column {col!r}: NaN is not a valid estimate")


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
    parser.add_argument(
        "--parameter-db",
        default=None,
        help="If given, validate the merged CSV against this parameter database.",
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

    if args.parameter_db is not None:
        _validate(merged, args.parameter_db)

    merged.to_csv(args.output, index=False)
    print(merged.to_string(index=False))


if __name__ == "__main__":
    main()
