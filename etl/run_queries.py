"""Step 4: run every query of sql/queries.sql and save the results.

    python -m etl.run_queries

Each result is printed and written to results/<query name>.md.
"""

import os
import re
import sys

import pandas as pd
from sqlalchemy import text

from etl.config import RESULTS_DIR, SQL_DIR
from etl.db import get_engine


def read_queries(path):
    """Split the file on the '-- name: xxx' lines -> {name: sql}."""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    parts = re.split(r"^-- name: *(\w+) *$", content, flags=re.M)
    # parts = [header, name1, sql1, name2, sql2, ...]
    return {name: sql.strip() for name, sql in zip(parts[1::2], parts[2::2])}


def main():
    # City names like Tōkyō break the default Windows console encoding.
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    engine = get_engine()
    queries = read_queries(os.path.join(SQL_DIR, "queries.sql"))

    with engine.connect() as conn:
        for name, sql in queries.items():
            df = pd.read_sql_query(text(sql), conn)
            table = df.to_markdown(index=False)
            print(f"\n## {name}\n\n{table}")
            with open(os.path.join(RESULTS_DIR, f"{name}.md"), "w", encoding="utf-8") as f:
                f.write(f"```sql\n{sql}\n```\n\n{table}\n")


if __name__ == "__main__":
    main()
