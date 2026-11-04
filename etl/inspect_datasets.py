"""Step 1: a first look at the raw datasets.

    python -m etl.inspect_datasets

For each CSV in data/raw: shape, columns, missing values and duplicate rows.
This is what told us, for example, that 4% of the monthly temperatures are
missing and that 251 cities have no population.
"""

import os

import pandas as pd

from etl.config import RAW_DIR


def main():
    for fname in sorted(os.listdir(RAW_DIR)):
        if not fname.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(RAW_DIR, fname), low_memory=False)
        print(f"\n=== {fname}: {df.shape[0]:,} rows x {df.shape[1]} columns")
        print(f"duplicate rows: {df.duplicated().sum()}")
        missing = df.isna().sum()
        print("missing values:")
        print(missing[missing > 0].to_string() if missing.any() else "  none")


if __name__ == "__main__":
    main()
