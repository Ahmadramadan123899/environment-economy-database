```sql
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
```

| city         | country   |   avg_temp_c |   years |
|:-------------|:----------|-------------:|--------:|
| Khartoum     | Sudan     |         29.4 |      64 |
| Niamey       | Niger     |         29.4 |      64 |
| Kassala      | Sudan     |         29.3 |      64 |
| Mopti        | Mali      |         29.2 |      64 |
| Kūstī        | Sudan     |         28.9 |      64 |
| Rabak        | Sudan     |         28.9 |      64 |
| Ambattūr     | India     |         28.9 |      64 |
| Tiruvottiyūr | India     |         28.9 |      64 |
| Āvadi        | India     |         28.9 |      64 |
| Tirupati     | India     |         28.9 |      64 |
