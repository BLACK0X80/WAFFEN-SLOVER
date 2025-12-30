"""
Git-related exceptions for Waffen-Solver.

Contains exceptions related to Git repository operations,
history analysis, and version control interactions.
"""

from pathlib import Path
from typing import Any, Dict

from waffen_solver.exceptions.base import WaffenSolverException


class GitException(WaffenSolverException):
    """
    Base exception for Git-related errors.

    Raised when general Git operations fail.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "GIT_ERROR",
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a GitException.

        Args:
            message: Description of the Git error.
            error_code: Specific error code for this Git error.
            details: Additional context about the failure.
        """
        super().__init__(message, error_code, details)


class RepositoryNotFoundException(GitException):
    """
    Raised when a Git repository cannot be found.

    Indicates the specified path does not contain
    a valid Git repository.
    """

    def __init__(
        self,
        path: Path | str,
        message: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a RepositoryNotFoundException.

        Args:
            path: The path where repository was expected.
            message: Optional custom message.
            details: Additional context about the search.
        """
        error_message = message or f"Git repository not found at: {path}"
        error_details = details or {}
        error_details["path"] = str(path)
        super().__init__(error_message, "REPOSITORY_NOT_FOUND", error_details)


class InvalidRepositoryException(GitException):
    """
    Raised when a repository is invalid or corrupted.

    Indicates the repository exists but is in an
    unusable state.
    """

    def __init__(
        self,
        path: Path | str,
        reason: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an InvalidRepositoryException.

        Args:
            path: The path to the invalid repository.
            reason: Why the repository is invalid.
            details: Additional context about the issue.
        """
        message = f"Invalid Git repository at: {path}"
        if reason:
            message = f"{message} - {reason}"
        error_details = details or {}
        error_details["path"] = str(path)
        if reason:
            error_details["reason"] = reason
        super().__init__(message, "INVALID_REPOSITORY", error_details)


class GitHistoryException(GitException):
    """
    Raised when Git history operations fail.

    Indicates issues with accessing or analyzing
    repository history.
    """

    def __init__(
        self,
        message: str,
        commit_ref: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a GitHistoryException.

        Args:
            message: Description of the history error.
            commit_ref: The commit reference involved, if any.
            details: Additional context about the failure.
        """
        error_details = details or {}
        if commit_ref:
            error_details["commit_ref"] = commit_ref
        super().__init__(message, "GIT_HISTORY_ERROR", error_details)
