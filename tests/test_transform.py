from datetime import datetime

import pytest
import sys
from pathlib import Path

# Add src directory to Python path - go up one level from tests/ to project root
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from transform import transform_rates


class TestTransformRates:
    """Test suite for the transform_rates function."""

    def test_successful_transformation(self):
        """Test successful transformation of typical API response."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {"EUR": 0.8454, "GBP": 0.7312, "JPY": 149.56},
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert len(result) == 3

        # Check EUR row
        eur_row = next(row for row in result if row["target_code"] == "EUR")
        assert eur_row["base_code"] == "USD"
        assert eur_row["target_code"] == "EUR"
        assert eur_row["rate"] == 0.8454
        assert eur_row["time_last_update_unix"] == 1750809600
        assert eur_row["time_next_update_unix"] == 1750896000
        assert isinstance(eur_row["time_last_update_utc"], datetime)
        assert isinstance(eur_row["time_next_update_utc"], datetime)

        # Check GBP row
        gbp_row = next(row for row in result if row["target_code"] == "GBP")
        assert gbp_row["base_code"] == "USD"
        assert gbp_row["target_code"] == "GBP"
        assert gbp_row["rate"] == 0.7312

        # Check JPY row
        jpy_row = next(row for row in result if row["target_code"] == "JPY")
        assert jpy_row["base_code"] == "USD"
        assert jpy_row["target_code"] == "JPY"
        assert jpy_row["rate"] == 149.56

    def test_datetime_parsing(self):
        """Test that datetime strings are correctly parsed."""
        # Arrange
        raw_data = {
            "base_code": "EUR",
            "time_last_update_utc": "Mon, 01 Jan 2024 12:30:45 +0000",
            "time_next_update_utc": "Tue, 02 Jan 2024 12:30:45 +0000",
            "time_last_update_unix": 1704110445,
            "time_next_update_unix": 1704196845,
            "conversion_rates": {"USD": 1.1025},
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert len(result) == 1
        row = result[0]

        # Check datetime objects
        assert isinstance(row["time_last_update_utc"], datetime)
        assert isinstance(row["time_next_update_utc"], datetime)

        # Check specific datetime values
        expected_last = datetime(2024, 1, 1, 12, 30, 45).replace(
            tzinfo=datetime.now().astimezone().tzinfo.utc,
        )
        expected_next = datetime(2024, 1, 2, 12, 30, 45).replace(
            tzinfo=datetime.now().astimezone().tzinfo.utc,
        )

        assert row["time_last_update_utc"].replace(
            tzinfo=None,
        ) == expected_last.replace(tzinfo=None)
        assert row["time_next_update_utc"].replace(
            tzinfo=None,
        ) == expected_next.replace(tzinfo=None)

    def test_empty_conversion_rates(self):
        """Test handling of empty conversion_rates."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {},
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert result == []
        assert len(result) == 0

    def test_missing_conversion_rates_key(self):
        """Test handling when conversion_rates key is missing."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            # No conversion_rates key
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert result == []
        assert len(result) == 0

    def test_single_currency_rate(self):
        """Test transformation with only one currency rate."""
        # Arrange
        raw_data = {
            "base_code": "GBP",
            "time_last_update_utc": "Wed, 23 Jun 2025 15:30:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 15:30:00 +0000",
            "time_last_update_unix": 1750829800,
            "time_next_update_unix": 1750916200,
            "conversion_rates": {"USD": 1.2684},
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert len(result) == 1
        row = result[0]
        assert row["base_code"] == "GBP"
        assert row["target_code"] == "USD"
        assert row["rate"] == 1.2684
        assert row["time_last_update_unix"] == 1750829800
        assert row["time_next_update_unix"] == 1750916200

    def test_many_currency_rates(self):
        """Test transformation with many currency rates."""
        # Arrange
        conversion_rates = {
            f"CUR{i:02d}": float(i * 0.1) for i in range(1, 101)
        }  # 100 currencies

        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": conversion_rates,
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert len(result) == 100

        # Check that all currencies are present
        target_codes = {row["target_code"] for row in result}
        expected_codes = {f"CUR{i:02d}" for i in range(1, 101)}
        assert target_codes == expected_codes

        # Check a few specific values
        cur01_row = next(row for row in result if row["target_code"] == "CUR01")
        assert cur01_row["rate"] == 0.1

        cur50_row = next(row for row in result if row["target_code"] == "CUR50")
        assert cur50_row["rate"] == 5.0

    def test_different_base_currencies(self):
        """Test transformation with different base currencies."""
        base_currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]

        for base_code in base_currencies:
            # Arrange
            raw_data = {
                "base_code": base_code,
                "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
                "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
                "time_last_update_unix": 1750809600,
                "time_next_update_unix": 1750896000,
                "conversion_rates": {"USD": 1.0, "EUR": 0.85},
            }

            # Act
            result = transform_rates(raw_data)

            # Assert
            assert len(result) == 2
            for row in result:
                assert row["base_code"] == base_code

    def test_invalid_datetime_format(self):
        """Test handling of invalid datetime format."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Invalid datetime format",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {"EUR": 0.8454},
        }

        # Act & Assert
        with pytest.raises(
            ValueError,
        ):  # datetime.strptime raises ValueError for invalid format
            transform_rates(raw_data)

    def test_missing_required_fields(self):
        """Test handling when required fields are missing."""
        # Test missing base_code
        with pytest.raises(KeyError):
            transform_rates(
                {
                    "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
                    "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
                    "time_last_update_unix": 1750809600,
                    "time_next_update_unix": 1750896000,
                    "conversion_rates": {"EUR": 0.8454},
                },
            )

        # Test missing time_last_update_utc
        with pytest.raises(KeyError):
            transform_rates(
                {
                    "base_code": "USD",
                    "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
                    "time_last_update_unix": 1750809600,
                    "time_next_update_unix": 1750896000,
                    "conversion_rates": {"EUR": 0.8454},
                },
            )

        # Test missing time_next_update_utc
        with pytest.raises(KeyError):
            transform_rates(
                {
                    "base_code": "USD",
                    "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
                    "time_last_update_unix": 1750809600,
                    "time_next_update_unix": 1750896000,
                    "conversion_rates": {"EUR": 0.8454},
                },
            )

    def test_numeric_rate_types(self):
        """Test handling of different numeric rate types."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {
                "EUR": 0.8454,  # float
                "JPY": 149,  # int
                "GBP": 0.7312000000,  # float with trailing zeros
                "CAD": 1.0,  # float that equals int
            },
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert len(result) == 4

        # Check that all rates are preserved as-is
        rates_dict = {row["target_code"]: row["rate"] for row in result}
        assert rates_dict["EUR"] == 0.8454
        assert rates_dict["JPY"] == 149
        assert rates_dict["GBP"] == 0.7312000000
        assert rates_dict["CAD"] == 1.0

    def test_logging_output(self, caplog):
        """Test that the function logs the correct information."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {"EUR": 0.8454, "GBP": 0.7312, "JPY": 149.56},
        }

        # Act
        with caplog.at_level("INFO"):
            result = transform_rates(raw_data)

        # Assert
        assert len(result) == 3
        assert "Transformed 3 currency rates rows" in caplog.text

    def test_logging_empty_rates(self, caplog):
        """Test logging when no rates are transformed."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {},
        }

        # Act
        with caplog.at_level("INFO"):
            result = transform_rates(raw_data)

        # Assert
        assert len(result) == 0
        assert "Transformed 0 currency rates rows" in caplog.text

    def test_row_structure_completeness(self):
        """Test that each transformed row has all required fields."""
        # Arrange
        raw_data = {
            "base_code": "USD",
            "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
            "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
            "time_last_update_unix": 1750809600,
            "time_next_update_unix": 1750896000,
            "conversion_rates": {"EUR": 0.8454, "GBP": 0.7312},
        }

        expected_fields = {
            "base_code",
            "target_code",
            "rate",
            "time_last_update_utc",
            "time_next_update_utc",
            "time_next_update_unix",
            "time_last_update_unix",
        }

        # Act
        result = transform_rates(raw_data)

        # Assert
        assert len(result) == 2
        for row in result:
            assert set(row.keys()) == expected_fields
            # Ensure no None values
            assert all(value is not None for value in row.values())

    def test_timezone_handling(self):
        """Test that timezones in datetime strings are handled correctly."""
        # Arrange - test different timezone formats
        test_cases = [
            "Wed, 23 Jun 2025 10:00:00 +0000",  # UTC
            "Wed, 23 Jun 2025 15:00:00 +0500",  # UTC+5
            "Wed, 23 Jun 2025 05:00:00 -0500",  # UTC-5
        ]

        for time_str in test_cases:
            raw_data = {
                "base_code": "USD",
                "time_last_update_utc": time_str,
                "time_next_update_utc": time_str,
                "time_last_update_unix": 1750809600,
                "time_next_update_unix": 1750896000,
                "conversion_rates": {"EUR": 0.8454},
            }

            # Act
            result = transform_rates(raw_data)

            # Assert
            assert len(result) == 1
            row = result[0]
            assert isinstance(row["time_last_update_utc"], datetime)
            assert isinstance(row["time_next_update_utc"], datetime)
            # Both should have timezone info
            assert row["time_last_update_utc"].tzinfo is not None
            assert row["time_next_update_utc"].tzinfo is not None


# Fixtures for common test data
@pytest.fixture
def sample_raw_data():
    """Fixture providing sample raw API data."""
    return {
        "base_code": "USD",
        "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
        "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
        "time_last_update_unix": 1750809600,
        "time_next_update_unix": 1750896000,
        "conversion_rates": {
            "EUR": 0.8454,
            "GBP": 0.7312,
            "JPY": 149.56,
            "CAD": 1.3421,
            "AUD": 1.4852,
        },
    }


# Parameterized tests for edge cases
@pytest.mark.parametrize("base_code", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"])
def test_various_base_codes(base_code):
    """Test transformation with various base currency codes."""
    raw_data = {
        "base_code": base_code,
        "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
        "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
        "time_last_update_unix": 1750809600,
        "time_next_update_unix": 1750896000,
        "conversion_rates": {"TEST": 1.23},
    }

    result = transform_rates(raw_data)

    assert len(result) == 1
    assert result[0]["base_code"] == base_code


@pytest.mark.parametrize("rate_value", [0.0, 0.0001, 1.0, 999999.99, 0.123456789])
def test_various_rate_values(rate_value):
    """Test transformation with various rate values."""
    raw_data = {
        "base_code": "USD",
        "time_last_update_utc": "Wed, 23 Jun 2025 10:00:00 +0000",
        "time_next_update_utc": "Thu, 24 Jun 2025 10:00:00 +0000",
        "time_last_update_unix": 1750809600,
        "time_next_update_unix": 1750896000,
        "conversion_rates": {"TEST": rate_value},
    }

    result = transform_rates(raw_data)

    assert len(result) == 1
    assert result[0]["rate"] == rate_value
