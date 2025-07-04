-- sql/insert_rates.sql
LOAD DATA LOCAL INFILE '{csv_file_path}'
INTO TABLE {table}
FIELDS TERMINATED BY ','
IGNORE 1 LINES
(
    base_code,
    target_code,
    rate,
    time_last_update_utc,
    time_next_update_utc,
    time_next_update_unix,
    time_last_update_unix
);
