CREATE TABLE rates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    base_code CHAR(3) NOT NULL,
    target_code CHAR(3) NOT NULL,
    rate DECIMAL(20,8) NOT NULL,
    time_last_update_utc DATETIME NOT NULL,
    time_next_update_utc DATETIME NOT NULL,
    time_last_update_unix BIGINT NOT NULL,
    time_next_update_unix BIGINT NOT NULL,
    row_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    row_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_rate (base_code, target_code, time_last_update_utc),
    INDEX idx_last_update_utc (time_last_update_utc)
);
