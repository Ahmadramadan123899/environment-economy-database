-- Analysis queries. Each one starts with "-- name:" so run_queries.py can
-- run them one by one and save the results.

-- name: q1_black_carbon_1995
-- Top 10 countries by black carbon (PM2.5) emissions in 1995.
SELECT c.name AS country, a.year, round(a.black_carbon)::bigint AS black_carbon_tonnes
FROM air_quality a
JOIN country c ON c.country_id = a.country_id
WHERE a.year = 1995 AND a.black_carbon IS NOT NULL
ORDER BY a.black_carbon DESC
LIMIT 10;

-- name: q2_cities_per_country
-- Number of cities, total and average city population per country.
-- Cities with unknown population are counted but not used in the sums.
SELECT c.name AS country,
       count(*) AS cities,
       sum(ci.population) AS total_population,
       round(avg(ci.population)) AS avg_city_population
FROM country c
JOIN city ci ON ci.country_id = c.country_id
GROUP BY c.name
ORDER BY cities DESC
LIMIT 10;

-- name: q3_gdp_growth
-- Fastest growing economies (GDP per capita), for countries with at least 30 years of data.
-- Ranked by the MEDIAN yearly growth, not the average: a few small territories
-- have broken values in the source (Turks and Caicos: +1205% in one year), and
-- one such year is enough to put a country first with an average.
SELECT c.name AS country,
       count(*) AS years,
       round(percentile_cont(0.5) WITHIN GROUP (ORDER BY e.gdp_growth)::numeric, 2) AS median_growth_pct,
       round(avg(e.gdp_growth)::numeric, 2) AS avg_growth_pct,
       round(min(e.gdp_growth)::numeric, 2) AS worst_year_pct,
       round(max(e.gdp_growth)::numeric, 2) AS best_year_pct
FROM economy e
JOIN country c ON c.country_id = e.country_id
GROUP BY c.name
HAVING count(*) >= 30
ORDER BY median_growth_pct DESC
LIMIT 10;

-- name: q4_hottest_cities
-- Hottest cities over 1950-2013.
SELECT ci.name AS city, c.name AS country,
       round(avg(cl.temperature_avg)::numeric, 1) AS avg_temp_c,
       count(*) AS years
FROM climate cl
JOIN city ci ON ci.city_id = cl.city_id
JOIN country c ON c.country_id = ci.country_id
GROUP BY ci.city_id, ci.name, c.name
ORDER BY avg(cl.temperature_avg) DESC
LIMIT 10;

-- name: q5_coldest_cities
SELECT ci.name AS city, c.name AS country,
       round(avg(cl.temperature_avg)::numeric, 1) AS avg_temp_c,
       count(*) AS years
FROM climate cl
JOIN city ci ON ci.city_id = cl.city_id
JOIN country c ON c.country_id = ci.country_id
GROUP BY ci.city_id, ci.name, c.name
ORDER BY avg(cl.temperature_avg)
LIMIT 10;

-- name: q6_big_cities_pollution
-- The 10 biggest cities with the emissions of their country (emissions are
-- only known per country, so cities of the same country share the value).
-- Averages are computed per country first, then joined, so each city counts once.
WITH country_air AS (
    SELECT country_id, avg(black_carbon) AS black_carbon, avg(nox) AS nox
    FROM air_quality
    GROUP BY country_id
)
SELECT ci.name AS city, c.name AS country, ci.population,
       round(ca.black_carbon) AS country_avg_black_carbon,
       round(ca.nox) AS country_avg_nox
FROM city ci
JOIN country c ON c.country_id = ci.country_id
LEFT JOIN country_air ca ON ca.country_id = ci.country_id
WHERE ci.population > 1000000
ORDER BY ci.population DESC
LIMIT 10;

-- name: q7_temperature_by_country
SELECT c.name AS country,
       count(DISTINCT ci.city_id) AS cities_tracked,
       round(avg(cl.temperature_avg)::numeric, 1) AS avg_temp_c,
       round(min(cl.temperature_avg)::numeric, 1) AS coldest_year_c,
       round(max(cl.temperature_avg)::numeric, 1) AS hottest_year_c
FROM climate cl
JOIN city ci ON ci.city_id = cl.city_id
JOIN country c ON c.country_id = ci.country_id
GROUP BY c.name
ORDER BY avg(cl.temperature_avg) DESC
LIMIT 10;

-- name: q8_lowest_emissions
-- Countries with the lowest average emissions. Small countries win, since
-- these are totals, not per person.
SELECT c.name AS country,
       count(*) AS years,
       round(avg(a.black_carbon)::numeric, 1) AS avg_black_carbon,
       round(avg(a.nox)::numeric, 1) AS avg_nox,
       round(avg(a.so2)::numeric, 1) AS avg_so2
FROM air_quality a
JOIN country c ON c.country_id = a.country_id
GROUP BY c.name
ORDER BY avg(a.black_carbon), avg(a.nox)
LIMIT 10;

-- name: q9_warming_by_country
-- Warming: average temperature in 2000-2012 minus 1950-1962, per country.
-- 2013 is left out because the data stops in the middle of that year.
-- Only countries with at least 5 cities, so one odd station does not decide.
WITH periods AS (
    SELECT ci.country_id,
           avg(cl.temperature_avg) FILTER (WHERE cl.year BETWEEN 1950 AND 1962) AS early,
           avg(cl.temperature_avg) FILTER (WHERE cl.year BETWEEN 2000 AND 2012) AS late,
           count(DISTINCT ci.city_id) AS cities
    FROM climate cl
    JOIN city ci ON ci.city_id = cl.city_id
    GROUP BY ci.country_id
)
SELECT c.name AS country, p.cities,
       round(p.early::numeric, 2) AS temp_1950s_c,
       round(p.late::numeric, 2) AS temp_2000s_c,
       round((p.late - p.early)::numeric, 2) AS warming_c
FROM periods p
JOIN country c ON c.country_id = p.country_id
WHERE p.cities >= 5 AND p.early IS NOT NULL AND p.late IS NOT NULL
ORDER BY warming_c DESC
LIMIT 10;

-- name: q10_growth_vs_emissions
-- Economy and pollution together: for countries with both, how GDP per capita
-- growth relates to the change in SO2 emissions between 1980 and 2010.
WITH gdp AS (
    SELECT country_id, avg(gdp_growth) AS avg_growth
    FROM economy
    WHERE year BETWEEN 1981 AND 2010
    GROUP BY country_id
    HAVING count(*) >= 25
),
so2 AS (
    SELECT country_id,
           max(so2) FILTER (WHERE year = 1980) AS so2_1980,
           max(so2) FILTER (WHERE year = 2010) AS so2_2010
    FROM air_quality
    GROUP BY country_id
)
SELECT c.name AS country,
       round(g.avg_growth::numeric, 2) AS avg_gdp_growth_pct,
       round((100 * (s.so2_2010 / s.so2_1980 - 1))::numeric) AS so2_change_pct
FROM gdp g
JOIN so2 s ON s.country_id = g.country_id
JOIN country c ON c.country_id = g.country_id
WHERE s.so2_1980 > 10000           -- big emitters only, small ones swing too much
ORDER BY g.avg_growth DESC
LIMIT 10;
