# utilities.py
from datetime import datetime


def get_current_date() -> str:
    """Get the current date in YYYY-MM-DD format."""
    date = datetime.now().strftime("%Y-%m-%d")
    return date
