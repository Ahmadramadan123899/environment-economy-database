```sql
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
```

| city        | country      |   population |   country_avg_black_carbon |   country_avg_nox |
|:------------|:-------------|-------------:|---------------------------:|------------------:|
| Tokyo       | Japan        |     37785000 |            82741           |       3.31989e+06 |
| Jakarta     | Indonesia    |     33756000 |           143368           |  953305           |
| Delhi       | India        |     32226000 |           541599           |       3.08731e+06 |
| Guangzhou   | China        |     26940000 |                1.15537e+06 |       9.43482e+06 |
| Mumbai      | India        |     24973000 |           541599           |       3.08731e+06 |
| Manila      | Philippines  |     24922000 |            31336           |  252247           |
| Shanghai    | China        |     24073000 |                1.15537e+06 |       9.43482e+06 |
| São Paulo   | Brazil       |     23086000 |           135526           |       1.56572e+06 |
| Seoul       | Korea, South |     23016000 |            40049           |  599287           |
| Mexico City | Mexico       |     21804000 |            53130           |       1.1599e+06  |
