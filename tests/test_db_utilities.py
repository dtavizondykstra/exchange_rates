# tests/test_db_utilities.py
import mysql.connector
import pytest
import sys
from pathlib import Path

# Add src directory to Python path - go up one level from tests/ to project root
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from db_utilities import connect_to_mysql, load_sql_template


def test_load_insert_rates_sql_template():
    """load_sql_template should find and return the contents of our
    sql/insert_rates.sql file in the project root.
    """
    content = load_sql_template("insert_rates.sql")
    # basic sanity check
    assert "LOAD DATA LOCAL INFILE" in content.upper()
    assert "{table}" in content  # make sure our placeholder is still there


def test_load_create_rates_table_sql_template():
    """Likewise, verify our DDL script is accessible."""
    content = load_sql_template("create_rates_table.sql")
    assert "CREATE TABLE" in content.upper()
    assert "rates" in content  # table name exists in the script


def test_connect_to_mysql_success(monkeypatch):
    """Should call mysql.connector.connect with the right parameters and return its result."""
    captured = {}

    class DummyConnection:
        def is_connected(self):
            return True

        def get_server_info(self):
            return "FAKE_VERSION"

    dummy = DummyConnection()

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return dummy

    monkeypatch.setattr(mysql.connector, "connect", fake_connect)

    db_cfg = {
        "host": "db.example.com",
        "user": "test_user",
        "password": "secret",
        "database": "exchange_rates",
    }

    conn = connect_to_mysql(db_cfg)

    # Should return our dummy object
    assert conn is dummy
    # And .is_connected() was called and returned True
    assert conn.is_connected()

    # Verify the connector was called with the expected arguments
    assert captured["host"] == "db.example.com"
    assert captured["user"] == "test_user"
    assert captured["password"] == "secret"
    assert captured["database"] == "exchange_rates"
    assert captured["allow_local_infile"] is True


def test_connect_to_mysql_missing_key():
    """If a required key is missing, Python should raise a KeyError."""
    incomplete_cfg = {
        "host": "db.example.com",
        # missing 'user'
        "password": "secret",
        "database": "exchange_rates",
    }
    with pytest.raises(KeyError):
        connect_to_mysql(incomplete_cfg)
