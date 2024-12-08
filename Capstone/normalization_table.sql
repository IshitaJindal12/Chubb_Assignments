CREATE TABLE normalized_target (
   Country_Name VARCHAR (255),
   Country_Code VARCHAR(50),
   Indicator_Name VARCHAR(255),
   Indicator_Code VARCHAR(255),
   Rec_year INT,
   Indicator_Value DECIMAL(28, 12)
);


select * from normalized_target;

truncate table normalized_target;
drop table normalized_target;