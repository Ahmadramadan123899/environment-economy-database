```sql
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
```

| country       |   cities_tracked |   avg_temp_c |   coldest_year_c |   hottest_year_c |
|:--------------|-----------------:|-------------:|-----------------:|-----------------:|
| Sudan         |                4 |         29.1 |             27.9 |             30.7 |
| Niger         |                3 |         28.4 |             26.4 |             30.4 |
| Burkina Faso  |                1 |         28.4 |             27.7 |             29.4 |
| Mali          |                3 |         28   |             26.7 |             30.2 |
| Chad          |                2 |         27.5 |             26.5 |             28.7 |
| Guinea-Bissau |                1 |         27.4 |             26.8 |             28.4 |
| Mauritania    |                1 |         27.4 |             26.3 |             28.7 |
| Qatar         |                1 |         27.3 |             26.2 |             28.9 |
| Nicaragua     |                4 |         27.3 |             26   |             28.7 |
| Benin         |                5 |         27.3 |             26.2 |             28.4 |
