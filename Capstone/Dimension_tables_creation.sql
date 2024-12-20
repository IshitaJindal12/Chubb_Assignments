CREATE TABLE DIM_COUNTRY (
    c_id INT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR(100),
    country_code VARCHAR(10),
	create_date DATETIME,
	update_date DATETIME
);

CREATE TABLE DIM_C_REGION (
    r_id INT IDENTITY(1,1) PRIMARY KEY,
    region VARCHAR(100),
	create_date DATETIME,
	update_date DATETIME
);

CREATE TABLE DIM_INCOME (
    inc_id INT IDENTITY(1,1) PRIMARY KEY,
    income VARCHAR(100),
);


CREATE TABLE DIM_YEARS (
    y_id INT IDENTITY(1,1) PRIMARY KEY,
    rec_year INT,
);


CREATE TABLE DIM_INDICATORS (
    i_id INT IDENTITY(1,1) PRIMARY KEY,
    indicator_code VARCHAR(255),
    indicator_name VARCHAR(255),
);



SELECT * FROM DIM_COUNTRY;
SELECT * FROM DIM_C_REGION;
SELECT * FROM DIM_INCOME;
SELECT * FROM DIM_YEARS;
SELECT * FROM DIM_INDICATORS;

TRUNCATE TABLE DIM_COUNTRY;

DROP TABLE DIM_INDICATORS;