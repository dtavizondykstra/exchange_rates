import logging
import sys
from pathlib import Path

import pytest

# Ensure we import the version under src/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import logging_utilities as lu


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    """
    1) Point lu.__file__ to tmp_path/src/logging_utilities.py
    2) Monkeypatch Path.resolve so setup_logging picks tmp_path as project_root
    3) Clear existing root logger handlers so basicConfig actually installs ours
    """
    # Create a fake src/logging_utilities.py under tmp_path
    fake_src = tmp_path / "src"
    fake_src.mkdir(parents=True)
    fake_mod = fake_src / "logging_utilities.py"
    fake_mod.write_text("# stub")

    # Override the module's __file__ so Path(__file__) uses fake_mod
    monkeypatch.setattr(lu, "__file__", str(fake_mod))

    # Replace Path.resolve: if resolving fake_mod, return fake_mod; else default
    original_resolve = Path.resolve

    def fake_resolve(self):
        if str(self) == str(fake_mod):
            return fake_mod
        return original_resolve(self)

    monkeypatch.setattr(Path, "resolve", fake_resolve)

    # Clear any handlers so basicConfig will run
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    yield

    # Teardown: restore Path.resolve
    monkeypatch.setattr(Path, "resolve", original_resolve)


def test_get_log_file_path(tmp_path):
    # Create the logs/ directory under fake src
    (tmp_path / "src" / "logs").mkdir(parents=True)

    p = lu.get_log_file_path("mylog")

    # It should live in a "logs" folder and be date-stamped
    assert p.parent.name == "logs"
    assert p.name.startswith("mylog_") and p.suffix == ".log"
    # File need not actually exist yet
    assert not p.exists()


def test_setup_logging_creates_file(tmp_path):
    logs_dir = tmp_path / "logs"
    assert not logs_dir.exists()

    # Call under our fake project_root
    lu.setup_logging("mylog")

    # Now there must be a logs/ folder with exactly one .log file
    assert logs_dir.exists()
    files = list(logs_dir.iterdir())
    assert len(files) == 1
    log_file = files[0]
    assert log_file.name.startswith("mylog_") and log_file.suffix == ".log"
