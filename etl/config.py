import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
CLEAN_DIR = os.path.join(ROOT, "data", "clean")
SQL_DIR = os.path.join(ROOT, "sql")
RESULTS_DIR = os.path.join(ROOT, "results")

# The temperature data stops in 2013 and the GDP data starts in 1950,
# so this is the period where all four datasets overlap.
FIRST_YEAR = 1950
LAST_YEAR = 2013
