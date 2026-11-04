```sql
-- Top 10 countries by black carbon (PM2.5) emissions in 1995.
SELECT c.name AS country, a.year, round(a.black_carbon)::bigint AS black_carbon_tonnes
FROM air_quality a
JOIN country c ON c.country_id = a.country_id
WHERE a.year = 1995 AND a.black_carbon IS NOT NULL
ORDER BY a.black_carbon DESC
LIMIT 10;
```

| country       |   year |   black_carbon_tonnes |
|:--------------|-------:|----------------------:|
| China         |   1995 |               1923864 |
| India         |   1995 |                660386 |
| United States |   1995 |                270097 |
| Indonesia     |   1995 |                197518 |
| Russia        |   1995 |                167610 |
| Brazil        |   1995 |                149386 |
| Japan         |   1995 |                125442 |
| Nigeria       |   1995 |                124020 |
| Pakistan      |   1995 |                 99356 |
| Germany       |   1995 |                 73818 |
