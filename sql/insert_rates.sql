-- sql/insert_rates.sql
LOAD DATA LOCAL INFILE '{csv_file_path}'
INTO TABLE {table}
FIELDS TERMINATED BY ','
IGNORE 1 LINES;
