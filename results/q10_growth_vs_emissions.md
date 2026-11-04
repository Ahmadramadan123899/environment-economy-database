```sql
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
```

| country      |   avg_gdp_growth_pct |   so2_change_pct |
|:-------------|---------------------:|-----------------:|
| Egypt        |                 6.86 |              123 |
| Korea, South |                 6.68 |              -73 |
| China        |                 6.25 |              161 |
| El Salvador  |                 6.15 |              249 |
| Botswana     |                 6.12 |              207 |
| Lebanon      |                 5.95 |               75 |
| Iran         |                 5.74 |              174 |
| Laos         |                 5.56 |              794 |
| Argentina    |                 5.32 |              -26 |
| Oman         |                 5.26 |              166 |
