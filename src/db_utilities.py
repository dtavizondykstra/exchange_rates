# db_utilities.py
"""Database utilities for exchange rates ETL pipeline."""

import logging
from pathlib import Path
from typing import Any

import mysql.connector
from retrying import retry

logger = logging.getLogger(__name__)


@retry(
    stop_max_attempt_number=3,
    wait_fixed=10000,
    retry_on_exception=lambda e: isinstance(e, mysql.connector.Error),
)
def connect_to_mysql(db_config: dict[str, Any]):
    """Establish and return a MySQL connection using db_config.

    Args:
        db_config: Dictionary containing database connection parameters

    Returns:
        MySQLConnection: Active database connection

    Raises:
        mysql.connector.Error: If connection fails
    """
    logger.info("Attempting to connect to MySQL database...")
    logger.info(
        "Connection details: %s@%s:%s/%s",
        db_config["user"],
        db_config["host"],
        db_config.get("port", 3306),
        db_config["database"],
    )

    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            port=db_config.get("port", 3306),
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            allow_local_infile=True,
            autocommit=False,
        )

        # Test the connection
        if connection.is_connected():
            server_info = connection.get_server_info()
            logger.info(f"Successfully connected to MySQL server version {server_info}")
            logger.info("Database connection established and ready for operations")
            return connection
        else:
            raise mysql.connector.Error("Connection established but not active")

    except mysql.connector.Error as db_error:
        error_code = getattr(db_error, "errno", "Unknown")
        error_msg = str(db_error)
        logger.error("Failed to connect to MySQL database")
        logger.error(f"Error Code: {error_code}")
        logger.error(f"Error Message: {error_msg}")

        # Provide more specific error messages based on common error codes
        if error_code == 1045:
            logger.error("Access denied - Check username and password")
        elif error_code == 2003:
            logger.error("Can't connect to MySQL server - Check host and port")
        elif error_code == 1049:
            logger.error("Unknown database - Check database name")
        elif error_code == 2002:
            logger.error("Connection timeout - Check network connectivity")

        raise
    except Exception as e:
        logger.error(f"Unexpected error during database connection: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise


def load_sql_template(name: str) -> str:
    """Load an SQL file from the sql/ directory by filename.

    Args:
        name: Name of the SQL file to load

    Returns:
        str: Contents of the SQL file

    Raises:
        FileNotFoundError: If the SQL file doesn't exist
        PermissionError: If the file cannot be read
    """
    path = Path(__file__).parent.parent / "sql" / name
    logger.info(f"Loading SQL template: {name}")
    logger.debug(f"Full path: {path}")

    try:
        if not path.exists():
            raise FileNotFoundError(f"SQL template file not found: {path}")

        sql = path.read_text(encoding="utf-8")
        logger.info(f"Successfully loaded SQL template: {name}")
        logger.debug(f"Template content length: {len(sql)} characters")
        return sql

    except FileNotFoundError:
        logger.error(f"SQL template file not found: {path}")
        raise
    except PermissionError:
        logger.error(f"Permission denied reading SQL template: {path}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading SQL template {name}: {e}")
        raise
