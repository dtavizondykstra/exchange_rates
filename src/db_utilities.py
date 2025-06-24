# db_utilities.py
"""Database utilities for exchange rates ETL pipeline."""

import logging
from pathlib import Path
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection

logger = logging.getLogger(__name__)


def connect_to_mysql(db_config: dict[str, Any]) -> MySQLConnection:
    """Establish and return a MySQL connection using db_config."""
    logger.info(
        "Connecting to MySQL %s@%s/%s",
        db_config["user"],
        db_config["host"],
        db_config["database"],
    )
    return mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        allow_local_infile=True,
    )


def load_sql_template(name: str) -> str:
    """Load an SQL file from the sql/ directory by filename."""
    path = Path(__file__).parent.parent / "sql" / name
    sql = path.read_text(encoding="utf-8")
    logger.debug("Loaded SQL template %s", path)
    return sql
