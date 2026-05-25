"""Print 'true' if parameter_db.csv's parameter rows differ from the
ones recorded in lattice_estimator_estimates.csv, else 'false'.

Used by the refresh-readme CI workflow to decide whether estimates
need re-running even when the lattice-estimator submodule has not moved.
"""
import csv
import sys

PARAM_COLS = ("ID", r"$\log_2(n)$", "σ", r"$\log_2(q)$", "$h$")
DB_PATH = "src/data/parameter_db.csv"
EST_PATH = "src/data/lattice_estimator_estimates.csv"


def _rows(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in PARAM_COLS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"{path}: missing columns {missing}")
        return sorted(tuple(r[c] for c in PARAM_COLS) for r in reader)


def main():
    db = _rows(DB_PATH)
    try:
        est = _rows(EST_PATH)
    except FileNotFoundError:
        # No cached estimates → refresh needed.
        print("true")
        return
    print("true" if db != est else "false")


if __name__ == "__main__":
    main()
