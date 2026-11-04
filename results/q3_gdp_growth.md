```sql
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
```

| country                  |   years |   median_growth_pct |   avg_growth_pct |   worst_year_pct |   best_year_pct |
|:-------------------------|--------:|--------------------:|-----------------:|-----------------:|----------------:|
| Singapore                |      53 |                8.13 |             6.75 |           -12.52 |           34.76 |
| Aruba                    |      43 |                7.57 |             4.57 |           -26.47 |           20.09 |
| Iraq                     |      43 |                7.11 |             5.59 |           -66.88 |           48.9  |
| Botswana                 |      53 |                6.85 |             6.8  |            -8.87 |           23.84 |
| Korea, South             |      60 |                6.54 |             6.09 |           -12.75 |           20.02 |
| Lebanon                  |      43 |                6.48 |             5.23 |           -57.72 |          116.79 |
| Macau                    |      43 |                6.4  |             7.82 |            -5.78 |           33.31 |
| Turks and Caicos Islands |      43 |                6.02 |            28.59 |           -95.99 |         1204.8  |
| China                    |      61 |                5.94 |             4.37 |           -14.21 |           13.66 |
| Oman                     |      43 |                5.8  |             5.47 |           -25.85 |           32.71 |
