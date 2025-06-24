#!/usr/bin/env python3
"""Exchange Rates ETL Pipeline - Main Entry Point.

This script orchestrates a complete ETL (Extract, Transform, Load) pipeline
for processing exchange rate data:

1. Extract: Fetches current exchange rate data from external APIs or uses
   sample data for testing
2. Transform: Processes and normalizes the raw API response into structured
   records for database storage
3. Load: Saves transformed data to CSV files and loads into MySQL database

The pipeline supports both live API data and sample data for testing purposes.
Configuration is managed through YAML files and environment variables.

Usage:
    python3 main.py

Configuration:
    - Environment variables: .env file (API keys, database credentials)
    - Application config: configs/default.yaml
    - Logging: Configured via logging_utilities module

Output:
    - CSV files: data/processed/rates_YYYY-MM-DD.csv
    - Database: MySQL table with exchange rate records
    - Logs: logs/main.log and console output
"""

import json
import logging
import sys
from datetime import date
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from config import (
    construct_api_url,
    load_configuration,
    load_database_config,
    load_environment,
)
from extract import get_exchange_rates
from load import load_csv_to_mysql
from transform import transform_rates
from data_utilities import save_to_csv
from logging_utilities import setup_logging


def main(use_sample: bool) -> None:
    setup_logging("main")
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Starting Exchange Rates ETL Pipeline")
    logger.info("=" * 60)
    logger.info(f"******* Running in {'sample' if use_sample else 'live'} data mode *******")

    try:
        # 1) Env, config, DB creds
        logger.info("Step 1: Loading configuration and environment variables")
        load_environment()
        cfg = load_configuration()
        db_cfg = load_database_config()
        logger.info("Configuration loaded successfully")

        # 2) Extract
        logger.info("Step 2: Extracting exchange rate data")
        if use_sample:
            sample_path = Path(__file__).parent / "data" / "raw" / "sample_rates.json"
            logger.info(f"Using sample JSON at {sample_path}")
            raw = json.loads(sample_path.read_text(encoding="utf-8"))
        else:
            url = construct_api_url(cfg)
            logger.info("Fetching live data from API")
            raw = get_exchange_rates(url)
        logger.info("Data extraction completed successfully")

        # 3) Transform
        logger.info("Step 3: Transforming exchange rate data")
        rows = transform_rates(raw)
        logger.info("Data transformation completed successfully")

        # 4) Save CSV
        logger.info("Step 4: Saving data to CSV file")
        out_dir = Path(__file__).parent / "data" / "processed"
        filename = f"rates_{date.today().isoformat()}.csv"
        csv_path = save_to_csv(rows, out_dir, filename)
        logger.info("CSV file saved successfully")

        # 5) Load into MySQL
        logger.info("Step 5: Loading data into MySQL database")
        load_csv_to_mysql(csv_path, db_cfg["table"], db_cfg)
        logger.info("Database loading completed successfully")

        logger.info("=" * 60)
        logger.info("Exchange Rates ETL Pipeline completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error("PIPELINE FAILED!")
        logger.error(f"Error: {e}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    main(use_sample=True)
