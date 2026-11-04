```sql
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
```

| country                           |   years |   avg_black_carbon |   avg_nox |   avg_so2 |
|:----------------------------------|--------:|-------------------:|----------:|----------:|
| Greenland                         |      64 |                0   |       8.3 |       2.8 |
| Guam                              |      64 |                0   |       0   |       0   |
| Liechtenstein                     |      64 |                0.4 |       1.8 |       0.3 |
| Saint Pierre and Miquelon         |      64 |                1.2 |     380.7 |      72.1 |
| Faroe Islands                     |      64 |                1.5 |      26   |       1.2 |
| Niue                              |      64 |                2.8 |      29.9 |      25.7 |
| Turks and Caicos Islands          |      64 |                3.3 |      51.9 |      48.2 |
| Falkland Islands (Islas Malvinas) |      64 |                4.4 |     297.3 |     100.3 |
| Montserrat                        |      64 |                4.9 |     213.4 |      51.3 |
| Virgin Islands, British           |      64 |                6.9 |     317.2 |      95.2 |
