# logging_utilities.py
"""Logging utilities for exchange rates ETL pipeline."""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_name: str) -> None:
    """Configure logging to write messages to stdout and log files."""
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    current_date = datetime.now().strftime("%d-%m-%Y")
    log_path = log_dir / f"{log_name}_{current_date}.log"

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, encoding="utf-8"),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def get_log_file_path(log_name: str) -> Path:
    """Get the path to the log file for the given log name."""
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        log_path = Path(__file__).parent / "logs" / f"{log_name}_{today}.log"
        return log_path
    except Exception as e:
        logging.error(f"Failed to get log file path: {e}")
        raise RuntimeError(f"Could not determine log file path for {log_name}") from e
