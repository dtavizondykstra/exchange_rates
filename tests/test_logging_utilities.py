# tests/test_logging_utilities.py

import logging
import sys
from pathlib import Path
from datetime import datetime

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging_utilities as lu


class DummyDateTime:
    """Fake datetime module with a fixed now()."""

    @classmethod
    def now(cls):
        # Use a reproducible date
        return datetime(2020, 1, 1, 12, 34, 56)

    @staticmethod
    def strftime(fmt):
        # Should match how strftime is used
        return "01-01-2020"  # dd-mm-YYYY


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    """
    Redirect the project_root to a temporary directory so we don't pollute real logs/.
    Also freeze datetime for reproducible filenames.
    """
    # Point __file__.resolve().parent.parent to tmp_path/project
    fake_src = tmp_path / "src"
    fake_src.mkdir(parents=True)
    fake_file = fake_src / "logging_utilities.py"
    fake_file.write_text("# dummy")
    # Monkeypatch Path.resolve to map the module's __file__ to fake_file
    original_resolve = Path.resolve

    def fake_resolve(self):
        # Only override for the module file path
        if str(self).endswith("logging_utilities.py"):
            return fake_file
        return original_resolve(self)

    monkeypatch.setattr(Path, "resolve", fake_resolve)

    # Freeze datetime in the module
    monkeypatch.setattr(lu, "datetime", DummyDateTime)

    yield

    # teardown: restore Path.resolve
    monkeypatch.setattr(Path, "resolve", original_resolve)


def test_get_log_file_path_produces_expected(tmp_path):
    # ensure logs/ exists under fake_src
    fake_logs = tmp_path / "src" / "logs"
    fake_logs.mkdir()

    # Call get_log_file_path
    p = lu.get_log_file_path("mylog")
    # It should point into fake_src/logs/mylog_01-01-2020.log
    assert p.name == "mylog_01-01-2020.log"
    assert "logs" in str(p)
    # The file does not have to exist yet
    assert not p.exists()


def test_setup_logging_creates_file_and_handlers(tmp_path):
    # Before calling, logs/ should not exist
    fake_logs = tmp_path / "logs"
    assert not fake_logs.exists()

    # Run setup
    lu.setup_logging("mylog")

    # Now logs/ and the date‐stamped file should exist
    log_file = tmp_path / "logs" / "mylog_01-01-2020.log"
    assert log_file.exists(), "Log file was not created"

    # And the root logger should have both a StreamHandler and a FileHandler
    handlers = logging.getLogger().handlers
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    assert any(isinstance(h, logging.FileHandler) for h in handlers)
