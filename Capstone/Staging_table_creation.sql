CREATE TABLE STG_VALUE_TABLE (
   Country_Name VARCHAR (255),
   Country_Code VARCHAR(50),
   Indicator_Name VARCHAR(255),
   Indicator_Code VARCHAR(255),
   Rec_Year INT,
   Indicator_Value DECIMAL(28, 12)
);

CREATE TABLE STG_COUNTRY_TABLE (
   Country_Code VARCHAR(10),
   Region VARCHAR (100),
   Income_Group VARCHAR(100),
   Special_Notes NVARCHAR(MAX),
   Table_Name VARCHAR(100),
);

CREATE TABLE STG_INDICATOR_TABLE(
   Indicator_Code VARCHAR(255),
   Indicator_Name VARCHAR(255),
   Source_Notes NVARCHAR(MAX),
   SOURCE_ORGANIZATION VARCHAR(255),
);



SELECT * from STG_VALUE_TABLE;
SELECT * from STG_INDICATOR_TABLE;
SELECT * from STG_COUNTRY_TABLE;

TRUNCATE TABLE STG_COUNTRY_TABLE;