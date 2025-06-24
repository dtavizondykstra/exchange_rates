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
    # 1) Read header and payload
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        data = [tuple(row[col] for col in columns) for row in reader]
    if not data:
        logger.warning("No rows to load from %s", csv_path)
        return

    # 2) Build SQL via template
    template = load_sql_template("insert_rates.sql")
    cols_sql = ", ".join(f"`{c}`" for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = template.format(
        table=table_name,
        columns=cols_sql,
        placeholders=placeholders,
        update_assignments=placeholders,
    )

    # 3) Execute
    conn = connect_to_mysql(db_config)
    cursor = conn.cursor()
    try:
        logger.info("Inserting %d rows into `%s`", len(data), table_name)
        cursor.executemany(sql, data)
        conn.commit()
        logger.info("Successfully loaded data into `%s`", table_name)
    except Exception as e:
        logger.error("Error loading data into MySQL: %s", e)
        raise
    finally:
        cursor.close()
        conn.close()
        logger.debug("MySQL connection closed")
