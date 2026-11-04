"""Step 3: create the tables and load the cleaned CSVs.

    python -m etl.load

The tables are emptied first, so running it twice gives the same result
instead of duplicates or "already exists" errors.
"""

import os

import pandas as pd
from sqlalchemy import column, table, text

from etl.config import CLEAN_DIR, SQL_DIR
from etl.db import get_engine

BATCH_SIZE = 1000  # one INSERT per 1000 rows instead of one per row


def add_ids(df, id_col):
    df = df.reset_index(drop=True)
    df.insert(0, id_col, range(1, len(df) + 1))
    return df


def attach_country_id(df, country_ids, what):
    """Replace the country name by its id. Rows with an unknown country are dropped."""
    df = df.assign(country_id=df["country"].map(country_ids))
    missing = df["country_id"].isna()
    if missing.any():
        # Mostly regions like "World" or "Africa" in the air pollution file,
        # which are not countries. Printed so nothing is lost silently.
        names = sorted(df.loc[missing, "country"].unique())
        print(f"  {what}: {missing.sum()} rows skipped, unknown country: {', '.join(names[:10])}"
              + (" ..." if len(names) > 10 else ""))
    df = df[~missing].copy()
    df["country_id"] = df["country_id"].astype(int)
    return df.drop(columns="country")


def city_lookup(cities):
    """(lowercase city name, country) -> city_id.

    Several cities can share a name inside one country (there are many
    Springfields in the US). The climate data does not say which one, so we
    take the biggest, which is almost always the one with weather records.
    Both the local name and the ASCII name are keys, since the climate file
    sometimes uses one and World Cities the other (Århus / Aarhus).
    """
    ordered = cities.sort_values("population", ascending=False, na_position="last")
    lookup = {}
    for row in ordered.itertuples():
        for name in (row.name, row.ascii_name):
            lookup.setdefault((str(name).lower(), row.country), row.city_id)
    return lookup


def insert(conn, table_name, df):
    # With a Core insert() SQLAlchemy sends real multi-row INSERTs
    # (INSERT ... VALUES (...), (...), ...). A plain text() query would still
    # go to the server one row at a time, which took minutes for the climate table.
    tbl = table(table_name, *[column(c) for c in df.columns])
    # Pandas NA -> None, so empty values become NULL in the database.
    records = df.astype(object).where(df.notna(), None).to_dict("records")
    for start in range(0, len(records), BATCH_SIZE):
        conn.execute(tbl.insert(), records[start:start + BATCH_SIZE])
    print(f"  {table_name:<12} {len(records):>8} rows")


def main():
    read = lambda name: pd.read_csv(os.path.join(CLEAN_DIR, name))
    engine = get_engine()

    with engine.begin() as conn:  # one transaction: all tables load, or none
        with open(os.path.join(SQL_DIR, "schema.sql"), encoding="utf-8") as f:
            # %% because the driver reads a single % as a parameter marker.
            conn.exec_driver_sql(f.read().replace("%", "%%"))
        conn.execute(text("TRUNCATE country, city, air_quality, climate, economy CASCADE"))

        print("loading:")
        countries = add_ids(read("countries.csv"), "country_id")
        insert(conn, "country", countries)
        country_ids = dict(zip(countries["name"], countries["country_id"]))

        cities = add_ids(read("cities.csv"), "city_id")
        cities["population"] = cities["population"].astype("Int64")
        lookup = city_lookup(cities)
        insert(conn, "city", attach_country_id(cities, country_ids, "city").drop(columns="ascii_name"))

        air = attach_country_id(read("air_quality.csv"), country_ids, "air_quality")
        insert(conn, "air_quality", add_ids(air, "aq_id"))

        economy = attach_country_id(read("economy.csv"), country_ids, "economy")
        insert(conn, "economy", add_ids(economy, "economy_id"))

        climate = read("climate.csv")
        keys = zip(climate["city"].str.lower(), climate["country"])
        climate["city_id"] = [lookup.get(k) for k in keys]
        matched = climate["city_id"].notna()
        print(f"  climate: {matched.mean():.1%} of the city-years matched a city "
              f"({climate.loc[~matched, ['city', 'country']].drop_duplicates().shape[0]} cities not found)")
        climate = climate[matched].astype({"city_id": int}).drop(columns=["city", "country"])
        insert(conn, "climate", add_ids(climate, "climate_id"))


if __name__ == "__main__":
    main()
