# load.py
"""Load module for exchange rates ETL pipeline."""

import csv
import logging
from pathlib import Path
from typing import Any

from db_utilities import connect_to_mysql, load_sql_template

logger = logging.getLogger(__name__)


def load_csv_to_mysql(
    csv_path: Path,
    table_name: str,
    db_config: dict[str, Any],
) -> None:
    """Read CSV and load data into MySQL table."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file {csv_path} does not exist")

    # 1) Validate CSV file and count rows
    logger.info(f"Analyzing CSV file: {csv_path}")

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            if not header:
                logger.warning(f"CSV file {csv_path} has no header row")
                return

            # Count data rows (excluding header)
            row_count = sum(1 for row in reader if row)  # Non-empty rows only

        except StopIteration:
            logger.warning(f"CSV file {csv_path} is empty")
            return

    if row_count == 0:
        logger.warning(f"CSV file {csv_path} has no data rows")
        return

    logger.info(f"Successfully validated CSV file: {csv_path}")
    logger.info(f"Header columns: {len(header)} ({', '.join(header[:5])}{'...' if len(header) > 5 else ''})")
    logger.info(f"Data rows to load: {row_count}")
    logger.info(f"Target table: {table_name}")

    # 2) Build SQL via template
    template = load_sql_template("insert_rates.sql")
    sql = template.format(
        csv_file_path=csv_path.as_posix(),
        table=table_name,
    )
    logger.info(f"Generated SQL: {sql}")

    # 3) Execute
    conn = connect_to_mysql(db_config)
    cursor = conn.cursor()
    try:
        logger.info(f"Executing SQL to load data into MySQL table: {table_name}")
        cursor.execute(sql)
        affected_rows = cursor.rowcount
        conn.commit()
        logger.info(f"Successfully loaded {affected_rows} rows into `{table_name}` table")
        logger.info(f"Expected: {row_count} rows, Loaded: {affected_rows} rows")
    except Exception as e:
        logger.info(f"Error loading data into `{table_name}` table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
        logger.info("MySQL connection closed")
