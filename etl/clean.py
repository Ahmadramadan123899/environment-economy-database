"""Step 2: clean the four raw datasets into one CSV per table.

    python -m etl.clean

Reads data/raw/*.csv and writes data/clean/*.csv. Nothing is invented: when a
value is missing we either keep it as NULL or drop the row, never fill it.
"""

import os

import pandas as pd

from etl.config import CLEAN_DIR, FIRST_YEAR, LAST_YEAR, RAW_DIR

# The datasets don't spell country names the same way. World Cities is our
# reference (it defines the country table), so we translate the other names
# to its spelling. Without this, South Korea, Myanmar, both Congos and others
# simply disappeared from the air quality, economy and climate tables.
COUNTRY_ALIASES = {
    "South Korea": "Korea, South",
    "North Korea": "Korea, North",
    "Myanmar": "Burma",
    "Congo": "Congo (Brazzaville)",
    "Democratic Republic of Congo": "Congo (Kinshasa)",
    "Congo (Democratic Republic Of The)": "Congo (Kinshasa)",
    "Cote d'Ivoire": "Côte d’Ivoire",
    "Côte D'Ivoire": "Côte d’Ivoire",
    "Bahamas": "Bahamas, The",
    "Gambia": "Gambia, The",
    "Cape Verde": "Cabo Verde",
    "Czech Republic": "Czechia",
    "Macedonia": "North Macedonia",
    "Swaziland": "Eswatini",
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Guinea Bissau": "Guinea-Bissau",
    "Timor": "Timor-Leste",
    "Macao": "Macau",
    "Curacao": "Curaçao",
    "Faeroe Islands": "Faroe Islands",
    "Falkland Islands": "Falkland Islands (Islas Malvinas)",
    "Micronesia (country)": "Micronesia, Federated States of",
    "Sint Maarten (Dutch part)": "Sint Maarten",
    "British Virgin Islands": "Virgin Islands, British",
    "United States Virgin Islands": "U.S. Virgin Islands",
}

# Air pollution dataset column -> our column. These are yearly emissions in
# tonnes per country (not concentrations in the air).
POLLUTANTS = {
    "Nitrogen Oxide": "nox",
    "Sulphur Dioxide": "so2",
    "Carbon Monoxide": "co",
    "NMVOCs": "nmvoc",
    "Ammonia": "nh3",
    "Black Carbon": "black_carbon",
}


def clean_country(names):
    """Strip spaces and translate to the World Cities spelling."""
    names = names.astype(str).str.strip()
    return names.replace(COUNTRY_ALIASES)


def in_period(df, col="year"):
    # 1950-2013 is the period covered by all four datasets (see README).
    return df[(df[col] >= FIRST_YEAR) & (df[col] <= LAST_YEAR)]


def clean_cities(world_cities):
    cities = pd.DataFrame({
        "name": world_cities["city"].astype(str).str.strip(),
        "ascii_name": world_cities["city_ascii"].astype(str).str.strip(),
        "country": clean_country(world_cities["country"]),
        # Missing population stays empty (NULL). A 0 would look like a real
        # value and pull down every average and sum.
        "population": world_cities["population"].astype("Int64"),
        "latitude": world_cities["lat"],
        "longitude": world_cities["lng"],
    })
    return cities.drop_duplicates().reset_index(drop=True)


def clean_countries(cities):
    names = cities["country"].dropna().drop_duplicates().sort_values()
    return names.reset_index(drop=True).to_frame(name="name")


def clean_air_quality(air):
    air = air.rename(columns={"Country": "country", "Year": "year", **POLLUTANTS})
    air["country"] = clean_country(air["country"])
    air["year"] = air["year"].astype(int)
    for col in POLLUTANTS.values():
        air[col] = pd.to_numeric(air[col], errors="coerce")
    air = in_period(air)
    # One row per country and year. The raw data already is, but summing makes
    # sure of it if two names were merged by the alias table.
    return (air.groupby(["country", "year"], as_index=False)[list(POLLUTANTS.values())]
            .sum(min_count=1))


def clean_economy(gdp):
    gdp = gdp.rename(columns={
        "Entity": "country",
        "Year": "year",
        "GDP per capita (output, multiple price benchmarks)": "gdp_per_capita",
    })
    gdp["country"] = clean_country(gdp["country"])
    gdp["year"] = gdp["year"].astype(int)
    gdp["gdp_per_capita"] = pd.to_numeric(gdp["gdp_per_capita"], errors="coerce")
    gdp = in_period(gdp).sort_values(["country", "year"])

    # Growth = change compared to the year before, in %. Only when the year
    # before really exists: if 1990 is missing, 1991 vs 1989 is not a yearly growth.
    by_country = gdp.groupby("country")
    previous = by_country["gdp_per_capita"].shift()
    consecutive = by_country["year"].diff() == 1
    gdp["gdp_growth"] = ((gdp["gdp_per_capita"] / previous - 1) * 100).where(consecutive)

    economy = gdp.dropna(subset=["gdp_growth"])
    return economy[["country", "year", "gdp_growth"]].reset_index(drop=True)


def clean_climate(path, chunksize=1_000_000):
    """Yearly average temperature per city.

    The raw file has 8.6 million monthly rows, so it is read in chunks to keep
    memory low. We group by city AND country: names like Barcelona, Cambridge
    or Alexandria exist in several countries and must not be averaged together.
    """
    sums = []
    columns = ["dt", "AverageTemperature", "City", "Country"]
    for chunk in pd.read_csv(path, usecols=columns, chunksize=chunksize):
        # About 4% of the months have no temperature. We drop them rather than guess.
        chunk = chunk.dropna(subset=["AverageTemperature"])
        chunk["year"] = chunk["dt"].str[:4].astype(int)
        chunk = in_period(chunk)
        chunk = chunk.assign(city=chunk["City"].str.strip(), country=clean_country(chunk["Country"]))
        sums.append(chunk.groupby(["city", "country", "year"])["AverageTemperature"].agg(["sum", "count"]))

    # A city's months can be split across two chunks, so we add up sums and
    # counts first and divide at the end.
    total = pd.concat(sums).groupby(level=[0, 1, 2]).sum()
    climate = (total["sum"] / total["count"]).rename("temperature_avg").reset_index()
    return climate


def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)

    def save(df, name):
        df.to_csv(os.path.join(CLEAN_DIR, name), index=False)
        print(f"{name:<16} {len(df):>8} rows")

    cities = clean_cities(pd.read_csv(os.path.join(RAW_DIR, "worldcities.csv")))
    save(clean_countries(cities), "countries.csv")
    save(cities, "cities.csv")
    save(clean_air_quality(pd.read_csv(os.path.join(RAW_DIR, "air-pollution.csv"))), "air_quality.csv")
    save(clean_economy(pd.read_csv(os.path.join(RAW_DIR, "gdp-per-capita-penn-world-table.csv"))), "economy.csv")
    save(clean_climate(os.path.join(RAW_DIR, "GlobalLandTemperaturesByCity.csv")), "climate.csv")


if __name__ == "__main__":
    main()
