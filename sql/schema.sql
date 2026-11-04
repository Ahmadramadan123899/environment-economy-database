-- 5 tables: country is the hub, city hangs off country, and the yearly
-- measures sit at the level where the data exists (pollution and GDP per
-- country, temperature per city). Safe to run again: nothing is recreated.

CREATE SCHEMA IF NOT EXISTS project;
SET search_path = project;

CREATE TABLE IF NOT EXISTS country (
    country_id  int PRIMARY KEY,
    name        varchar(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS city (
    city_id     int PRIMARY KEY,
    name        varchar(100) NOT NULL,
    population  int,            -- NULL when unknown
    latitude    real,
    longitude   real,
    country_id  int NOT NULL REFERENCES country (country_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Emissions in tonnes per year, for one country and one year.
CREATE TABLE IF NOT EXISTS air_quality (
    aq_id         int PRIMARY KEY,
    year          int NOT NULL,
    nox           real,          -- nitrogen oxides
    so2           real,          -- sulphur dioxide
    co            real,          -- carbon monoxide
    nmvoc         real,          -- non-methane volatile organic compounds
    nh3           real,          -- ammonia
    black_carbon  real,          -- part of PM2.5
    country_id    int NOT NULL REFERENCES country (country_id) ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE (country_id, year)    -- one record per country per year
);

CREATE TABLE IF NOT EXISTS climate (
    climate_id       int PRIMARY KEY,
    year             int NOT NULL,
    temperature_avg  real,       -- yearly average of the monthly averages, in °C
    city_id          int NOT NULL REFERENCES city (city_id) ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE (city_id, year)
);

CREATE TABLE IF NOT EXISTS economy (
    economy_id  int PRIMARY KEY,
    year        int NOT NULL,
    gdp_growth  real,            -- % change of GDP per capita vs the year before
    country_id  int NOT NULL REFERENCES country (country_id) ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE (country_id, year)
);

-- PostgreSQL does not index foreign keys by itself, and every query joins on them.
CREATE INDEX IF NOT EXISTS city_country_idx ON city (country_id);

COMMENT ON TABLE country     IS 'Countries, as named in the World Cities dataset';
COMMENT ON TABLE city        IS 'Cities with population and coordinates';
COMMENT ON TABLE air_quality IS 'Air pollutant emissions (tonnes) per country and year, 1950-2013';
COMMENT ON TABLE climate     IS 'Average temperature per city and year, 1950-2013';
COMMENT ON TABLE economy     IS 'GDP per capita growth per country and year, 1950-2013';
