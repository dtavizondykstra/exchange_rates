from unittest.mock import MagicMock

import pytest
import requests
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Fix the import - import the specific function from the module
from extract import get_exchange_rates


class TestGetExchangeRates:
    """Test suite for the get_exchange_rates function."""

    def test_successful_request(self, monkeypatch):
        """Test successful API request returns expected data."""
        # Arrange
        expected_data = {
            "rates": {"USD": 1.0, "EUR": 0.85, "GBP": 0.73},
            "base": "USD",
            "date": "2025-06-23",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = expected_data

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act
        result = get_exchange_rates(url)

        # Assert
        assert result == expected_data

    def test_custom_timeout(self, monkeypatch):
        """Test that custom timeout parameter is passed correctly."""
        # Arrange
        expected_data = {"test": "data"}
        timeout_used = None

        def mock_get(*args, **kwargs):
            nonlocal timeout_used
            timeout_used = kwargs.get("timeout")
            return MagicMock(
                status_code=200,
                raise_for_status=lambda: None,
                json=lambda: expected_data,
            )

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"
        custom_timeout = 30.0

        # Act
        get_exchange_rates(url, timeout=custom_timeout)

        # Assert
        assert timeout_used == custom_timeout

    def test_default_timeout(self, monkeypatch):
        """Test that default timeout is used when not specified."""
        # Arrange
        expected_data = {"test": "data"}
        timeout_used = None

        def mock_get(*args, **kwargs):
            nonlocal timeout_used
            timeout_used = kwargs.get("timeout")
            return MagicMock(
                status_code=200,
                raise_for_status=lambda: None,
                json=lambda: expected_data,
            )

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"

        # Act
        get_exchange_rates(url)

        # Assert
        assert timeout_used == 10.0

    def test_http_error_with_status_code(self, monkeypatch):
        """Test handling of HTTP errors with status codes."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("Not Found")

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act & Assert
        with pytest.raises(requests.HTTPError):
            get_exchange_rates(url)

    def test_connection_error(self, monkeypatch):
        """Test handling of connection errors."""

        # Arrange
        def mock_get(*args, **kwargs):
            raise requests.ConnectionError("Connection failed")

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"

        # Act & Assert
        with pytest.raises(requests.ConnectionError):
            get_exchange_rates(url)

    def test_timeout_error(self, monkeypatch):
        """Test handling of timeout errors."""

        # Arrange
        def mock_get(*args, **kwargs):
            raise requests.Timeout("Request timed out")

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"

        # Act & Assert
        with pytest.raises(requests.Timeout):
            get_exchange_rates(url)

    def test_request_exception_without_response(self, monkeypatch):
        """Test handling of RequestException without response attribute."""

        # Arrange
        def mock_get(*args, **kwargs):
            raise requests.RequestException("Generic request error")

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"

        # Act & Assert
        with pytest.raises(requests.RequestException):
            get_exchange_rates(url)

    def test_raise_for_status_called(self, monkeypatch):
        """Test that raise_for_status is called and json is not called on error.

        Note: Due to the @retry decorator, this will be called 3 times before
        failing.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad status")
        mock_response.json.return_value = {"should": "not be called"}

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act & Assert
        with pytest.raises(requests.HTTPError):
            get_exchange_rates(url)

        # Verify raise_for_status was called 3 times due to retry decorator
        assert mock_response.raise_for_status.call_count == 3
        # Verify json was not called since raise_for_status failed
        mock_response.json.assert_not_called()

    def test_empty_response_data(self, monkeypatch):
        """Test handling of empty but valid JSON response."""
        # Arrange
        empty_data = {}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = empty_data

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act
        result = get_exchange_rates(url)

        # Assert
        assert result == empty_data

    def test_json_decode_error(self, monkeypatch):
        """Test handling of invalid JSON in response."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act & Assert
        with pytest.raises(ValueError):
            get_exchange_rates(url)

    def test_logging_success(self, monkeypatch, caplog):
        """Test that successful requests are logged correctly."""
        # Arrange
        expected_data = {"test": "data"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = expected_data

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act
        with caplog.at_level("INFO"):
            get_exchange_rates(url)

        # Assert
        assert f"Fetching rates from {url}" in caplog.text
        assert "Successfully fetched exchange rates" in caplog.text

    def test_logging_error_with_status_code(self, monkeypatch, caplog):
        """Test that errors with status codes are logged correctly."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server Error")

        # Create an HTTPError with a response attribute
        http_error = requests.HTTPError("Server Error")
        http_error.response = mock_response

        def mock_get(*args, **kwargs):
            raise http_error

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"

        # Act & Assert
        with caplog.at_level("INFO"):
            with pytest.raises(requests.HTTPError):
                get_exchange_rates(url)

        # Assert logging
        assert f"Fetching rates from {url}" in caplog.text
        assert "Error fetching exchange rates" in caplog.text
        assert "status=500" in caplog.text

    def test_logging_error_no_status_code(self, monkeypatch, caplog):
        """Test error logging when response has no status_code."""

        # Arrange
        def mock_get(*args, **kwargs):
            raise requests.ConnectionError("No connection")

        monkeypatch.setattr("extract.requests.get", mock_get)

        url = "https://api.example.com/rates"

        # Act & Assert
        with caplog.at_level("INFO"):
            with pytest.raises(requests.ConnectionError):
                get_exchange_rates(url)

        # Assert logging
        assert f"Fetching rates from {url}" in caplog.text
        assert "Error fetching exchange rates" in caplog.text
        assert "status=N/A" in caplog.text

    def test_url_parameter_passed_correctly(self, monkeypatch):
        """Test that the URL parameter is passed correctly to requests.get."""
        # Arrange
        expected_data = {"test": "data"}
        url_used = None

        def mock_get(url, **kwargs):
            nonlocal url_used
            url_used = url
            return MagicMock(
                status_code=200,
                raise_for_status=lambda: None,
                json=lambda: expected_data,
            )

        monkeypatch.setattr("extract.requests.get", mock_get)

        test_url = "https://api.example.com/rates"

        # Act
        get_exchange_rates(test_url)

        # Assert
        assert url_used == test_url

    def test_complex_response_data(self, monkeypatch):
        """Test handling of complex nested response data."""
        # Arrange
        complex_data = {
            "success": True,
            "timestamp": 1687526400,
            "base": "USD",
            "date": "2025-06-23",
            "rates": {
                "EUR": 0.8454,
                "GBP": 0.7312,
                "JPY": 149.56,
                "CAD": 1.3421,
                "AUD": 1.4852,
                "CHF": 0.9023,
            },
            "historical": False,
            "source": "https://exchangerate-api.com",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = complex_data

        monkeypatch.setattr(
            "extract.requests.get",
            lambda *args, **kwargs: mock_response,
        )

        url = "https://api.example.com/rates"

        # Act
        result = get_exchange_rates(url)

        # Assert
        assert result == complex_data
        assert result["rates"]["EUR"] == 0.8454
        assert len(result["rates"]) == 6


# Integration-style tests (commented out by default)
class TestGetExchangeRatesIntegration:
    """Integration tests for get_exchange_rates function.

    Note: These tests are commented out by default as they require real HTTP calls.
    Uncomment and modify URLs for actual integration testing.
    """

    @pytest.mark.skip(reason="Integration test - requires real API")
    def test_real_api_call(self):
        """Test with a real API endpoint (httpbin for testing)."""
        url = "https://httpbin.org/json"
        result = get_exchange_rates(url)
        assert isinstance(result, dict)

    @pytest.mark.skip(reason="Integration test - requires real API")
    def test_real_timeout(self):
        """Test timeout with a real slow endpoint."""
        url = "https://httpbin.org/delay/5"  # 5 second delay
        with pytest.raises(requests.Timeout):
            get_exchange_rates(url, timeout=1.0)


# Fixtures for common test data
@pytest.fixture
def sample_exchange_data():
    """Fixture providing sample exchange rate data."""
    return {
        "rates": {
            "USD": 1.0,
            "EUR": 0.8454,
            "GBP": 0.7312,
            "JPY": 149.56,
            "CAD": 1.3421,
        },
        "base": "USD",
        "date": "2025-06-23",
    }


@pytest.fixture
def sample_url():
    """Fixture providing a sample API URL."""
    return "https://api.exchangerate-api.com/v4/latest/USD"


# Parameterized tests for different error scenarios
@pytest.mark.parametrize(
    "exception_class,exception_message",
    [
        (requests.ConnectionError, "Connection refused"),
        (requests.Timeout, "Request timed out"),
        (requests.HTTPError, "HTTP 500 Error"),
        (requests.RequestException, "Generic request error"),
    ],
)
def test_various_request_exceptions(monkeypatch, exception_class, exception_message):
    """Test handling of various request exceptions."""

    # Arrange
    def mock_get(*args, **kwargs):
        raise exception_class(exception_message)

    monkeypatch.setattr("extract.requests.get", mock_get)

    url = "https://api.example.com/rates"

    # Act & Assert
    with pytest.raises(exception_class):
        get_exchange_rates(url)


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500, 502, 503])
def test_various_http_status_codes(monkeypatch, status_code):
    """Test handling of various HTTP status codes."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        f"HTTP {status_code}",
    )

    monkeypatch.setattr(
        "extract.requests.get",
        lambda *args, **kwargs: mock_response,
    )

    url = "https://api.example.com/rates"

    # Act & Assert
    with pytest.raises(requests.HTTPError):
        get_exchange_rates(url)
