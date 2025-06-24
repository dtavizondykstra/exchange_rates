# data_utilities.py
"""Data utilities for exchange rates ETL pipeline."""

import csv
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def save_to_csv(rows: list[dict[str, Any]], output_dir: Path, filename: str) -> Path:
    """Write a list of dicts out to CSV in output_dir/filename."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename

    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Saved {len(rows)} rows to {file_path}")
    return file_path
