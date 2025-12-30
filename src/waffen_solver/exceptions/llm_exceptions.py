"""
LLM-related exceptions for Waffen-Solver.

Contains exceptions related to language model operations,
API interactions, and response handling.
"""

from typing import Any, Dict

from waffen_solver.exceptions.base import WaffenSolverException


class LLMException(WaffenSolverException):
    """
    Base exception for LLM-related errors.

    Raised when general LLM operations fail.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "LLM_ERROR",
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an LLMException.

        Args:
            message: Description of the LLM error.
            error_code: Specific error code for this LLM error.
            details: Additional context about the failure.
        """
        super().__init__(message, error_code, details)


class RateLimitException(LLMException):
    """
    Raised when API rate limits are exceeded.

    Indicates the system should wait before
    making additional requests.
    """

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: int | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a RateLimitException.

        Args:
            message: Description of the rate limit.
            retry_after: Seconds to wait before retry.
            details: Additional context about the limit.
        """
        error_details = details or {}
        if retry_after is not None:
            error_details["retry_after_seconds"] = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", error_details)
        self._retry_after = retry_after

    @property
    def retry_after(self) -> int | None:
        """Get recommended wait time in seconds."""
        return self._retry_after


class InvalidResponseException(LLMException):
    """
    Raised when LLM response is invalid or malformed.

    Indicates the response could not be parsed or
    did not meet expected format requirements.
    """

    def __init__(
        self,
        message: str = "Invalid LLM response received",
        response_preview: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an InvalidResponseException.

        Args:
            message: Description of what was invalid.
            response_preview: Truncated preview of response.
            details: Additional context about the issue.
        """
        error_details = details or {}
        if response_preview:
            error_details["response_preview"] = response_preview[:200]
        super().__init__(message, "INVALID_LLM_RESPONSE", error_details)


class TokenLimitException(LLMException):
    """
    Raised when token limits are exceeded.

    Indicates the input or output exceeded the
    maximum allowed tokens.
    """

    def __init__(
        self,
        message: str = "Token limit exceeded",
        token_count: int | None = None,
        max_tokens: int | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a TokenLimitException.

        Args:
            message: Description of the token limit issue.
            token_count: Actual number of tokens.
            max_tokens: Maximum allowed tokens.
            details: Additional context about the limit.
        """
        error_details = details or {}
        if token_count is not None:
            error_details["token_count"] = token_count
        if max_tokens is not None:
            error_details["max_tokens"] = max_tokens
        super().__init__(message, "TOKEN_LIMIT_EXCEEDED", error_details)
