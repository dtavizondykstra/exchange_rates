# extract.py
"""Extract module for exchange rates ETL pipeline."""

import logging
from collections.abc import Mapping
from typing import Any

import requests
from retrying import retry

logger = logging.getLogger(__name__)


@retry(
    stop_max_attempt_number=3,
    wait_fixed=10000,
    retry_on_exception=lambda e: isinstance(e, requests.RequestException),
)
def get_exchange_rates(url: str, timeout: float = 10.0) -> Mapping[str, Any]:
    """Fetch exchange rates from the API endpoint."""
    try:
        logger.info(f"Fetching rates from {url[:30]}***.. (truncated for security)")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        logger.info("Successfully fetched exchange rates")
    except requests.RequestException as e:
        status = getattr(e.response, "status_code", "N/A")
        logger.error(f"Error fetching exchange rates (status={status}): {e}")
        raise
    return response.json()
