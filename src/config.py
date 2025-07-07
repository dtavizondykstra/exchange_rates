# config.py
"""Configuration management for exchange rates ETL pipeline."""

import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_environment(env_path: Path | None = None) -> None:
    """Load environment variables from a .env file."""
    try:
        logger.info("Loading environment variables from .env file")
        if env_path is not None:
            load_dotenv(dotenv_path=str(env_path))
        else:
            default_env = Path.cwd() / ".env"
            load_dotenv(dotenv_path=str(default_env))
        logger.info(".env file loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load .env file: {e}")
        raise


def load_configuration(config_path: Path | None = None) -> dict:
    """Read YAML configuration and return it as a dict."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "configs" / "default.yaml"

    try:
        logger.info(f"Loading configuration from YAML file: {config_path}")
        with Path.open(config_path) as f:
            cfg = yaml.safe_load(f)
        logger.info("Configuration loaded successfully")
        return cfg
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML configuration: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise


def construct_api_url(config: dict) -> str:
    """Construct API URL from configuration."""
    try:
        api_config = config["api"]
        base_url = api_config["base_url"]
        endpoint = api_config["endpoint"]

        api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not api_key:
            raise ValueError("EXCHANGE_RATE_API_KEY environment variable is not set")

        # Construct the full URL
        url = f"{base_url}/{api_key}/{endpoint}"

        logger.info(f"Constructed API URL: {url.replace(api_key, '*******')}")
        return url
    except KeyError as e:
        logger.error(f"Missing required configuration key: {e}")
        raise
    except Exception as e:
        logger.error(f"Error constructing API URL: {e}")
        raise


def load_database_config() -> dict:
    """Load database configuration from environment variables."""
    try:
        logger.info("Loading database configuration from environment variables")
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "table": os.getenv("DB_TABLE", "exchange_rates"),
        }

        # Validate required fields
        required_fields = ["database", "user", "password"]
        missing_fields = [field for field in required_fields if not db_config[field]]
        if missing_fields:
            raise ValueError(f"Missing required database configuration: {missing_fields}")

        logger.info("Database configuration loaded successfully")
        return db_config
    except ValueError as e:
        logger.error(f"Database configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading database configuration: {e}")
        raise


def get_slack_token() -> str:
    """Retrieve Slack token from environment variable."""
    slack_token = os.getenv("BOT_TOKEN")
    if not slack_token:
        raise ValueError("BOT_TOKEN environment variable is not set")
    return slack_token
