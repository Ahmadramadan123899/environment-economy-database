```sql
SELECT ci.name AS city, c.name AS country,
       round(avg(cl.temperature_avg)::numeric, 1) AS avg_temp_c,
       count(*) AS years
FROM climate cl
JOIN city ci ON ci.city_id = cl.city_id
JOIN country c ON c.country_id = ci.country_id
GROUP BY ci.city_id, ci.name, c.name
ORDER BY avg(cl.temperature_avg)
LIMIT 10;
```

| city           | country       |   avg_temp_c |   years |
|:---------------|:--------------|-------------:|--------:|
| Norilsk        | Russia        |        -11.4 |      64 |
| Kyzyl          | Russia        |         -5.5 |      64 |
| Chita          | Russia        |         -3.6 |      64 |
| Surgut         | Russia        |         -2.9 |      64 |
| Nefteyugansk   | Russia        |         -2.9 |      64 |
| Ulaanbaatar    | Mongolia      |         -2.6 |      64 |
| Bratsk         | Russia        |         -2.1 |      64 |
| Anchorage      | United States |         -1.8 |      64 |
| Yakeshi        | China         |         -1.8 |      64 |
| Nizhnevartovsk | Russia        |         -1.7 |      64 |
