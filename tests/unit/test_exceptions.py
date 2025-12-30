"""
Unit tests for exception classes.
"""

import pytest
from datetime import datetime

from waffen_solver.exceptions import (
    WaffenSolverException,
    AnalysisException,
    ErrorParsingException,
    RootCauseNotFoundException,
    InsufficientContextException,
    GitException,
    RepositoryNotFoundException,
    InvalidRepositoryException,
    GitHistoryException,
    LLMException,
    RateLimitException,
    InvalidResponseException,
    TokenLimitException,
)


class TestWaffenSolverException:
    """Tests for base exception."""

    def test_basic_creation(self) -> None:
        """Test basic exception creation."""
        exc = WaffenSolverException("Test error")
        assert exc.message == "Test error"
        assert exc.error_code == "WAFFEN_ERROR"
        assert isinstance(exc.timestamp, datetime)

    def test_custom_error_code(self) -> None:
        """Test exception with custom error code."""
        exc = WaffenSolverException("Error", error_code="CUSTOM_CODE")
        assert exc.error_code == "CUSTOM_CODE"

    def test_details(self) -> None:
        """Test exception with details."""
        details = {"key": "value", "count": 42}
        exc = WaffenSolverException("Error", details=details)
        assert exc.details == details

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        exc = WaffenSolverException("Error", error_code="CODE")
        result = exc.to_dict()
        assert result["message"] == "Error"
        assert result["error_code"] == "CODE"
        assert "timestamp" in result

    def test_user_message(self) -> None:
        """Test user-friendly message."""
        exc = WaffenSolverException("Error occurred", error_code="ERR001")
        assert exc.get_user_message() == "[ERR001] Error occurred"


class TestAnalysisExceptions:
    """Tests for analysis exceptions."""

    def test_analysis_exception(self) -> None:
        """Test basic analysis exception."""
        exc = AnalysisException("Analysis failed")
        assert exc.error_code == "ANALYSIS_ERROR"

    def test_error_parsing_exception(self) -> None:
        """Test error parsing exception."""
        exc = ErrorParsingException("Parse failed", raw_error="bad input")
        assert exc.error_code == "ERROR_PARSING_FAILED"
        assert exc.details["raw_error"] == "bad input"

    def test_root_cause_not_found(self) -> None:
        """Test root cause not found exception."""
        exc = RootCauseNotFoundException(analyzed_error="some error")
        assert exc.error_code == "ROOT_CAUSE_NOT_FOUND"

    def test_insufficient_context(self) -> None:
        """Test insufficient context exception."""
        exc = InsufficientContextException(required_context=["file", "line"])
        assert exc.error_code == "INSUFFICIENT_CONTEXT"
        assert "file" in exc.details["required_context"]


class TestGitExceptions:
    """Tests for Git exceptions."""

    def test_git_exception(self) -> None:
        """Test basic Git exception."""
        exc = GitException("Git error")
        assert exc.error_code == "GIT_ERROR"

    def test_repository_not_found(self) -> None:
        """Test repository not found exception."""
        exc = RepositoryNotFoundException("/path/to/repo")
        assert exc.error_code == "REPOSITORY_NOT_FOUND"
        assert exc.details["path"] == "/path/to/repo"

    def test_invalid_repository(self) -> None:
        """Test invalid repository exception."""
        exc = InvalidRepositoryException("/repo", reason="Corrupted")
        assert exc.error_code == "INVALID_REPOSITORY"
        assert exc.details["reason"] == "Corrupted"

    def test_git_history_exception(self) -> None:
        """Test Git history exception."""
        exc = GitHistoryException("History error", commit_ref="abc123")
        assert exc.error_code == "GIT_HISTORY_ERROR"


class TestLLMExceptions:
    """Tests for LLM exceptions."""

    def test_llm_exception(self) -> None:
        """Test basic LLM exception."""
        exc = LLMException("LLM error")
        assert exc.error_code == "LLM_ERROR"

    def test_rate_limit_exception(self) -> None:
        """Test rate limit exception."""
        exc = RateLimitException(retry_after=60)
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.retry_after == 60

    def test_invalid_response_exception(self) -> None:
        """Test invalid response exception."""
        exc = InvalidResponseException(response_preview="abc" * 100)
        assert exc.error_code == "INVALID_LLM_RESPONSE"
        assert len(exc.details["response_preview"]) <= 200

    def test_token_limit_exception(self) -> None:
        """Test token limit exception."""
        exc = TokenLimitException(token_count=5000, max_tokens=4096)
        assert exc.error_code == "TOKEN_LIMIT_EXCEEDED"
        assert exc.details["token_count"] == 5000
        assert exc.details["max_tokens"] == 4096
