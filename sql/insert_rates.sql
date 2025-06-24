-- sql/insert_rates.sql

INSERT INTO `{table}` ({columns})
VALUES ({placeholders})
ON DUPLICATE KEY UPDATE
{update_assignments};
