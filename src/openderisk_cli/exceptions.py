"""Custom exceptions for OpenDerisk CLI."""

from typing import Optional


class OpenDeriskError(Exception):
    """Base exception for OpenDerisk CLI."""

    def __init__(
        self, message: str, details: Optional[str] = None, suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details
        self.suggestion = suggestion

    def __str__(self) -> str:
        parts = [self.message]
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return "\n".join(parts)


class ConfigError(OpenDeriskError):
    """Configuration error."""

    pass


class APIError(OpenDeriskError):
    """API error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[dict] = None,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__(message, details, suggestion)
        self.status_code = status_code
        self.response = response or {}


class ValidationError(OpenDeriskError):
    """Parameter validation error."""

    pass


class TimeoutError(OpenDeriskError):
    """Timeout error."""

    pass
