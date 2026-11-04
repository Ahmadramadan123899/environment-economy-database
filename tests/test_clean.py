import pandas as pd
import pytest

from etl.clean import clean_air_quality, clean_cities, clean_climate, clean_country, clean_economy
from etl.load import city_lookup
from etl.run_queries import read_queries


def test_country_aliases():
    names = pd.Series([" South Korea ", "Myanmar", "France"])
    assert list(clean_country(names)) == ["Korea, South", "Burma", "France"]


def test_missing_population_stays_empty():
    raw = pd.DataFrame({
        "city": ["A", "B"], "city_ascii": ["A", "B"], "country": ["X", "X"],
        "population": [1000, None], "lat": [0, 1], "lng": [0, 1],
    })
    cities = clean_cities(raw)
    assert cities["population"].isna().sum() == 1  # not replaced by 0


def test_gdp_growth_needs_the_previous_year():
    gdp = pd.DataFrame({
        "Entity": ["X"] * 4,
        "Year": [1950, 1951, 1953, 1954],  # 1952 is missing
        "GDP per capita (output, multiple price benchmarks)": [100, 110, 120, 132],
    })
    eco = clean_economy(gdp)
    assert list(eco["year"]) == [1951, 1954]  # no growth for 1953 (no 1952 to compare with)
    assert eco["gdp_growth"].tolist() == pytest.approx([10.0, 10.0])


def test_air_quality_keeps_1950_to_2013():
    air = pd.DataFrame({
        "Country": ["X", "X", "X"], "Year": [1900, 1990, 2015],
        "Nitrogen Oxide": [1, 2, 3], "Sulphur Dioxide": [1, 2, 3], "Carbon Monoxide": [1, 2, 3],
        "NMVOCs": [1, 2, 3], "Ammonia": [1, 2, 3], "Black Carbon": [1, 2, 3],
    })
    assert list(clean_air_quality(air)["year"]) == [1990]


def test_same_city_name_in_two_countries_is_not_mixed(tmp_path):
    path = tmp_path / "temps.csv"
    pd.DataFrame({
        "dt": ["1990-01-01", "1990-02-01", "1990-01-01"],
        "AverageTemperature": [10.0, 12.0, 30.0],
        "City": ["Barcelona", "Barcelona", "Barcelona"],
        "Country": ["Spain", "Spain", "Venezuela"],
    }).to_csv(path, index=False)
    # chunksize=1 also checks that averages are right across chunks
    climate = clean_climate(path, chunksize=1).set_index("country")["temperature_avg"]
    assert climate["Spain"] == 11.0
    assert climate["Venezuela"] == 30.0


def test_city_lookup_prefers_biggest_city_and_ascii_name():
    cities = pd.DataFrame({
        "city_id": [1, 2, 3],
        "name": ["Springfield", "Springfield", "Århus"],
        "ascii_name": ["Springfield", "Springfield", "Aarhus"],
        "country": ["United States", "United States", "Denmark"],
        "population": [50_000, 160_000, None],
    })
    lookup = city_lookup(cities)
    assert lookup[("springfield", "United States")] == 2
    assert lookup[("aarhus", "Denmark")] == 3
    assert lookup[("århus", "Denmark")] == 3


def test_every_query_has_a_name():
    queries = read_queries("sql/queries.sql")
    assert len(queries) == 10
    assert all(sql.rstrip().endswith(";") for sql in queries.values())
