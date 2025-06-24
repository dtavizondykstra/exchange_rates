# logging_utilities.py
"""Logging utilities for exchange rates ETL pipeline."""

import logging
import sys
from pathlib import Path


def setup_logging(log_name: str) -> None:
    """Configure logging to write messages to stdout and log files."""
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"{log_name}.log"

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
