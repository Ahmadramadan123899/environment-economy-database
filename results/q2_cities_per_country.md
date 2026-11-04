```sql
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
```

| country        |   cities |   total_population |   avg_city_population |
|:---------------|---------:|-------------------:|----------------------:|
| India          |     7108 |          514693978 |                 72461 |
| United States  |     5344 |          379426737 |                 71001 |
| Brazil         |     2961 |          191184513 |                 64655 |
| Germany        |     1759 |           68218046 |                 38804 |
| China          |     1732 |         1360845815 |                793959 |
| Philippines    |     1583 |          137686398 |                 87254 |
| United Kingdom |     1365 |           64991494 |                 47613 |
| Italy          |     1357 |           42129508 |                 31046 |
| Japan          |     1344 |          184894147 |                137570 |
| France         |     1160 |           43786135 |                 37747 |
