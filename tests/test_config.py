import os
import pytest
import yaml
import sys
from pathlib import Path

# Add src directory to Python path - go up one level from tests/ to project root
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from config import (
    load_configuration,
    load_database_config,
    load_environment,
)


def test_load_configuration(tmp_path):
    # dump a minimal YAML
    cfg = {"api": {"base_url": "http://x"}, "etl": {"base_currency": "ABC"}}
    f = tmp_path / "cfg.yaml"
    f.write_text(yaml.safe_dump(cfg))
    loaded = load_configuration(config_path=f)
    assert loaded["api"]["base_url"] == "http://x"
    assert loaded["etl"]["base_currency"] == "ABC"


def test_load_database_config(monkeypatch):
    # set all required env vars
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "1234")
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_NAME", "d")
    monkeypatch.setenv("DB_TABLE", "t")
    db = load_database_config()
    assert db["host"] == "h"
    assert db["port"] == 1234
    assert db["table"] == "t"


def test_missing_db_env(monkeypatch):
    monkeypatch.delenv("DB_USER", raising=False)
    with pytest.raises(ValueError, match="Missing required database configuration"):
        load_database_config()


def test_load_environment_reads_dotenv(tmp_path, monkeypatch):
    # Create a .env file in a temp dir
    env_file = tmp_path / ".env"
    env_file.write_text("MY_TEST_VAR=hello_world\n")

    # Make sure our cwd is that temp dir
    monkeypatch.chdir(tmp_path)
    # Ensure it isn't already set
    monkeypatch.delenv("MY_TEST_VAR", raising=False)

    # Should pick up MY_TEST_VAR from ./.env
    load_environment()
    assert os.getenv("MY_TEST_VAR") == "hello_world"


def test_load_environment_with_explicit_path(tmp_path, monkeypatch):
    # Create a custom env file
    custom = tmp_path / "custom.env"
    custom.write_text("CUSTOM_VAR=42\n")

    # Ensure it's not set yet
    monkeypatch.delenv("CUSTOM_VAR", raising=False)

    # Call with explicit path (requires load_environment to pass env_path into load_dotenv)
    load_environment(env_path=custom)
    assert os.getenv("CUSTOM_VAR") == "42"


def test_load_environment_raises_on_error(monkeypatch):
    # Force load_dotenv() to throw - fix the import reference
    import config as cfg_mod

    monkeypatch.setattr(
        cfg_mod,
        "load_dotenv",
        lambda *a, **kw: (_ for _ in ()).throw(Exception("boom")),
    )

    with pytest.raises(Exception) as exc:
        load_environment()
    assert "boom" in str(exc.value)
