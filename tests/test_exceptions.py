"""Tests for custom exceptions."""

import pytest

from openderisk_cli.exceptions import (
    APIError,
    ConfigError,
    OpenDeriskError,
    TimeoutError,
    ValidationError,
)


class TestOpenDeriskError:
    """Tests for OpenDeriskError base exception."""

    def test_message_only(self) -> None:
        """Test exception with message only."""
        error = OpenDeriskError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.details is None
        assert error.suggestion is None
        assert str(error) == "Something went wrong"

    def test_with_details(self) -> None:
        """Test exception with message and details."""
        error = OpenDeriskError("Error occurred", details="More info here")
        assert error.message == "Error occurred"
        assert error.details == "More info here"
        assert "Details: More info here" in str(error)

    def test_with_suggestion(self) -> None:
        """Test exception with message and suggestion."""
        error = OpenDeriskError("Error occurred", suggestion="Try again")
        assert error.message == "Error occurred"
        assert error.suggestion == "Try again"
        assert "Suggestion: Try again" in str(error)

    def test_with_all_fields(self) -> None:
        """Test exception with all fields."""
        error = OpenDeriskError("Error occurred", details="More info", suggestion="Try again")
        assert error.message == "Error occurred"
        assert error.details == "More info"
        assert error.suggestion == "Try again"

        error_str = str(error)
        assert "Error occurred" in error_str
        assert "Details: More info" in error_str
        assert "Suggestion: Try again" in error_str

    def test_is_exception(self) -> None:
        """Test that OpenDeriskError is an Exception."""
        error = OpenDeriskError("Test error")
        assert isinstance(error, Exception)


class TestConfigError:
    """Tests for ConfigError."""

    def test_inherits_from_base(self) -> None:
        """Test that ConfigError inherits from OpenDeriskError."""
        error = ConfigError("Config error")
        assert isinstance(error, OpenDeriskError)
        assert isinstance(error, Exception)

    def test_with_all_fields(self) -> None:
        """Test ConfigError with all fields."""
        error = ConfigError(
            "Invalid configuration",
            details="Missing required field",
            suggestion="Check config file",
        )
        assert error.message == "Invalid configuration"
        assert error.details == "Missing required field"
        assert error.suggestion == "Check config file"


class TestAPIError:
    """Tests for APIError."""

    def test_basic_error(self) -> None:
        """Test basic APIError."""
        error = APIError("API request failed")
        assert error.message == "API request failed"
        assert error.status_code is None
        assert error.response == {}

    def test_with_status_code(self) -> None:
        """Test APIError with status code."""
        error = APIError("Not found", status_code=404)
        assert error.message == "Not found"
        assert error.status_code == 404

    def test_with_response(self) -> None:
        """Test APIError with response data."""
        response_data = {"error": "Invalid request", "code": "BAD_REQUEST"}
        error = APIError("Bad request", response=response_data)
        assert error.response == response_data

    def test_with_all_fields(self) -> None:
        """Test APIError with all fields."""
        error = APIError(
            "Server error",
            status_code=500,
            response={"error": "Internal server error"},
            details="Database connection failed",
            suggestion="Contact support",
        )
        assert error.message == "Server error"
        assert error.status_code == 500
        assert error.response == {"error": "Internal server error"}
        assert error.details == "Database connection failed"
        assert error.suggestion == "Contact support"

    def test_inherits_from_base(self) -> None:
        """Test that APIError inherits from OpenDeriskError."""
        error = APIError("Test")
        assert isinstance(error, OpenDeriskError)


class TestValidationError:
    """Tests for ValidationError."""

    def test_inherits_from_base(self) -> None:
        """Test that ValidationError inherits from OpenDeriskError."""
        error = ValidationError("Invalid input")
        assert isinstance(error, OpenDeriskError)

    def test_with_details(self) -> None:
        """Test ValidationError with details."""
        error = ValidationError(
            "Invalid parameter",
            details="Name must be at least 3 characters",
            suggestion="Provide a longer name",
        )
        assert error.message == "Invalid parameter"
        assert error.details == "Name must be at least 3 characters"


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_inherits_from_base(self) -> None:
        """Test that TimeoutError inherits from OpenDeriskError."""
        error = TimeoutError("Request timed out")
        assert isinstance(error, OpenDeriskError)

    def test_with_all_fields(self) -> None:
        """Test TimeoutError with all fields."""
        error = TimeoutError(
            "Connection timed out",
            details="No response after 30 seconds",
            suggestion="Check your network connection",
        )
        assert error.message == "Connection timed out"
        assert error.details == "No response after 30 seconds"
        assert error.suggestion == "Check your network connection"
