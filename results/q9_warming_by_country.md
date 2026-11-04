```sql
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
```

| country     |   cities |   temp_1950s_c |   temp_2000s_c |   warming_c |
|:------------|---------:|---------------:|---------------:|------------:|
| Kazakhstan  |       13 |           3.76 |           5.24 |        1.49 |
| Iran        |       54 |          14.98 |          16.36 |        1.38 |
| Uzbekistan  |        7 |          11.6  |          12.95 |        1.35 |
| Russia      |      143 |           3.5  |           4.82 |        1.32 |
| Belarus     |        7 |           6.41 |           7.61 |        1.2  |
| Ukraine     |       15 |           7.99 |           9.16 |        1.17 |
| Lithuania   |        5 |           6.31 |           7.47 |        1.17 |
| Finland     |        5 |           3.97 |           5.11 |        1.13 |
| Poland      |       36 |           7.85 |           8.95 |        1.09 |
| Netherlands |       23 |           9.27 |          10.35 |        1.08 |
