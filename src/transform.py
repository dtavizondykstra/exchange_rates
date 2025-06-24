# transform.py
"""Transform module for exchange rates ETL pipeline."""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def transform_rates(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the API JSON into a list of dicts matching database schema."""
    rows: list[dict[str, Any]] = []

    # parse the UTC strings into Python datetimes
    last_utc = datetime.strptime(
        raw["time_last_update_utc"],
        "%a, %d %b %Y %H:%M:%S %z",
    )
    next_utc = datetime.strptime(
        raw["time_next_update_utc"],
        "%a, %d %b %Y %H:%M:%S %z",
    )

    common = {
        "base_code": raw["base_code"],
        "time_last_update_utc": last_utc,
        "time_next_update_utc": next_utc,
        "time_next_update_unix": raw["time_next_update_unix"],
        "time_last_update_unix": raw["time_last_update_unix"],
    }

    for target_code, rate in raw.get("conversion_rates", {}).items():
        row = {
            "base_code": common["base_code"],
            "target_code": target_code,
            "rate": rate,
            "time_last_update_utc": common["time_last_update_utc"],
            "time_next_update_utc": common["time_next_update_utc"],
            "time_next_update_unix": common["time_next_update_unix"],
            "time_last_update_unix": common["time_last_update_unix"],
        }
        rows.append(row)

    logger.info(f"Transformed {len(rows)} currency rates rows")
    return rows
