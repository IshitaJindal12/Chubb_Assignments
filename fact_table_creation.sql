CREATE TABLE FACT_INDICATOR_VALUES (
    fact_id INT PRIMARY KEY,
    country_id INT,
    region_id INT,
    income_id INT,
    year_id INT,
    indicator_id INT,
    indicator_value DECIMAL(28,12),
    create_date DATETIME,
    update_date DATETIME,
    FOREIGN KEY (country_id) REFERENCES DIM_COUNTRY(c_id),
    FOREIGN KEY (region_id) REFERENCES DIM_C_REGION(r_id),
    FOREIGN KEY (income_id) REFERENCES DIM_INCOME(inc_id),
    FOREIGN KEY (year_id) REFERENCES DIM_YEARS(y_id),
    FOREIGN KEY (indicator_id) REFERENCES DIM_INDICATORS(i_id)
);

SELECT * FROM FACT_INDICATOR_VALUES;