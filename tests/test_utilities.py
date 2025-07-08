# test_utilities.py
import sys
from pathlib import Path
from datetime import datetime
import re

# Ensure we import the version under src/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import utilities


def test_get_current_date_fixed(monkeypatch):
    # Freeze datetime.now() to a known value
    fixed = datetime(2021, 12, 31, 23, 59, 59)

    class DummyDateTime:
        @classmethod
        def now(cls):
            return fixed

        @staticmethod
        def strftime(fmt):
            return fixed.strftime(fmt)

    # Override the imported datetime in utilities
    monkeypatch.setattr(utilities, "datetime", DummyDateTime)

    # Now get_current_date should return the fixed date in YYYY-MM-DD
    result = utilities.get_current_date()
    assert result == "2021-12-31"


def test_get_current_date_format():
    # Without patching, it should return today's date in the correct format
    result = utilities.get_current_date()
    assert isinstance(result, str)
    # Check pattern YYYY-MM-DD
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", result) is not None
