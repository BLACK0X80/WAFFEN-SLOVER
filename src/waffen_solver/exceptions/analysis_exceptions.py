"""
Analysis-related exceptions for Waffen-Solver.

Contains exceptions related to error analysis, parsing,
and root cause identification operations.
"""

from typing import Any, Dict

from waffen_solver.exceptions.base import WaffenSolverException


class AnalysisException(WaffenSolverException):
    """
    Base exception for analysis-related errors.

    Raised when general analysis operations fail.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "ANALYSIS_ERROR",
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an AnalysisException.

        Args:
            message: Description of the analysis error.
            error_code: Specific error code for this analysis error.
            details: Additional context about the failure.
        """
        super().__init__(message, error_code, details)


class ErrorParsingException(AnalysisException):
    """
    Raised when error message parsing fails.

    Indicates the system could not parse or understand
    the provided error message format.
    """

    def __init__(
        self,
        message: str,
        raw_error: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an ErrorParsingException.

        Args:
            message: Description of the parsing failure.
            raw_error: The original error text that failed to parse.
            details: Additional context about the failure.
        """
        error_details = details or {}
        if raw_error:
            error_details["raw_error"] = raw_error
        super().__init__(message, "ERROR_PARSING_FAILED", error_details)


class RootCauseNotFoundException(AnalysisException):
    """
    Raised when root cause cannot be determined.

    Indicates analysis completed but could not identify
    the underlying cause of the error.
    """

    def __init__(
        self,
        message: str = "Could not determine root cause of error",
        analyzed_error: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a RootCauseNotFoundException.

        Args:
            message: Description of why root cause was not found.
            analyzed_error: The error that was analyzed.
            details: Additional context about the analysis.
        """
        error_details = details or {}
        if analyzed_error:
            error_details["analyzed_error"] = analyzed_error
        super().__init__(message, "ROOT_CAUSE_NOT_FOUND", error_details)


class InsufficientContextException(AnalysisException):
    """
    Raised when there is not enough context for analysis.

    Indicates more information is needed to perform
    accurate error analysis.
    """

    def __init__(
        self,
        message: str = "Insufficient context for accurate analysis",
        required_context: list[str] | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an InsufficientContextException.

        Args:
            message: Description of what context is missing.
            required_context: List of context items needed.
            details: Additional information about requirements.
        """
        error_details = details or {}
        if required_context:
            error_details["required_context"] = required_context
        super().__init__(message, "INSUFFICIENT_CONTEXT", error_details)
