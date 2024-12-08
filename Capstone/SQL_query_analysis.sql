/* No duplicate records in the fact table */
SELECT country_id, region_id, income_id, year_id, indicator_id, COUNT(*) AS duplicate_count
FROM FACT_INDICATOR_VALUES
GROUP BY country_id, region_id, income_id, year_id, indicator_id
HAVING COUNT(*) > 1;


/* Validate data completeness for each year */
SELECT y.rec_year, COUNT(fi.year_id) AS fact_count
FROM DIM_YEARS y
LEFT JOIN FACT_INDICATOR_VALUES fi ON y.y_id = fi.year_id
GROUP BY y.rec_year
ORDER BY y.rec_year;


/* Indicator trends over time */
SELECT y.rec_year, i.indicator_name, AVG(fi.indicator_value) AS avg_value
FROM FACT_INDICATOR_VALUES fi
JOIN DIM_YEARS y ON fi.year_id = y.y_id
JOIN DIM_INDICATORS i ON fi.indicator_id = i.i_id
GROUP BY y.rec_year, i.indicator_name
ORDER BY y.rec_year, avg_value DESC;


/* Average indicator value by region over the years */
SELECT r.region, y.rec_year, i.indicator_name, AVG(fi.indicator_value) AS avg_indicator_value
FROM FACT_INDICATOR_VALUES fi
JOIN DIM_C_REGION r ON fi.region_id = r.r_id
JOIN DIM_YEARS y ON fi.year_id = y.y_id
JOIN DIM_INDICATORS i ON fi.indicator_id = i.i_id
WHERE r.region IS NOT NULL
GROUP BY r.region, y.rec_year, i.indicator_name
ORDER BY r.region, y.rec_year, avg_indicator_value DESC;


/* Regional Indicator Performance Across Income Groups */
SELECT r.region,inc.income,i.indicator_name, AVG(fi.indicator_value) AS avg_indicator_value
FROM FACT_INDICATOR_VALUES fi
JOIN DIM_C_REGION r ON fi.region_id = r.r_id
JOIN DIM_INCOME inc ON fi.income_id = inc.inc_id
JOIN DIM_INDICATORS i ON fi.indicator_id = i.i_id
WHERE r.region IS NOT NULL
GROUP BY r.region, inc.income, i.indicator_name
ORDER BY r.region, inc.income, avg_indicator_value DESC;