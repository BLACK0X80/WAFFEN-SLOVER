"""
Base exception classes for Waffen-Solver.

Provides the foundation exception class from which all other
Waffen-Solver exceptions inherit.
"""

from datetime import datetime
from typing import Any, Dict


class WaffenSolverException(Exception):
    """
    Base exception for all Waffen-Solver errors.

    Provides structured error information including error codes,
    details, and timestamps for comprehensive error tracking.

    Attributes:
        error_code: Unique identifier for the error type.
        details: Additional context about the error.
        timestamp: When the error occurred.
        message: Human-readable error message.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "WAFFEN_ERROR",
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a WaffenSolverException.

        Args:
            message: Human-readable error description.
            error_code: Unique identifier for categorizing errors.
            details: Additional error context as key-value pairs.
        """
        super().__init__(message)
        self._message = message
        self._error_code = error_code
        self._details = details or {}
        self._timestamp = datetime.now()

    @property
    def error_code(self) -> str:
        """Get the error code."""
        return self._error_code

    @property
    def details(self) -> Dict[str, Any]:
        """Get error details dictionary."""
        return self._details

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp when error occurred."""
        return self._timestamp

    @property
    def message(self) -> str:
        """Get the error message."""
        return self._message

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary representation.

        Returns:
            Dictionary containing all exception attributes.
        """
        return {
            "error_code": self._error_code,
            "message": self._message,
            "details": self._details,
            "timestamp": self._timestamp.isoformat(),
        }

    def get_user_message(self) -> str:
        """
        Get a user-friendly error message.

        Returns:
            Formatted message suitable for display to end users.
        """
        return f"[{self._error_code}] {self._message}"
