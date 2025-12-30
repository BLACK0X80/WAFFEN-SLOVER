"""
Logging utilities for Waffen-Solver.

Provides structured logging with configurable
output and formatting.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from waffen_solver.config.settings import VerbosityLevel


class LogFormatter(logging.Formatter):
    """
    Custom log formatter with structured output.

    Provides consistent formatting for all log messages.
    """

    FORMAT_TEMPLATE = "[{timestamp}] [{level}] {name}: {message}"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record.

        Args:
            record: Log record to format.

        Returns:
            Formatted log string.
        """
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        return self.FORMAT_TEMPLATE.format(
            timestamp=timestamp,
            level=record.levelname,
            name=record.name,
            message=record.getMessage(),
        )


class WaffenSolverLogger:
    """
    Structured logging for all operations.

    Provides logging methods for different operation types
    with consistent formatting and output handling.

    Attributes:
        logger: Underlying Python logger.
        verbosity: Current verbosity level.
    """

    _instances: Dict[str, "WaffenSolverLogger"] = {}

    def __init__(
        self,
        name: str = "waffen_solver",
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
        log_file: Optional[Path] = None,
    ) -> None:
        """
        Initialize the logger.

        Args:
            name: Logger name.
            verbosity: Verbosity level.
            log_file: Optional file to log to.
        """
        self._name = name
        self._verbosity = verbosity
        self._logger = logging.getLogger(name)
        self._configure_logger(log_file)

    @classmethod
    def get_instance(
        cls,
        name: str = "waffen_solver",
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
    ) -> "WaffenSolverLogger":
        """
        Get or create a logger instance.

        Args:
            name: Logger name.
            verbosity: Verbosity level.

        Returns:
            Logger instance.
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name, verbosity)
        return cls._instances[name]

    @property
    def verbosity(self) -> VerbosityLevel:
        """Get current verbosity level."""
        return self._verbosity

    def _configure_logger(self, log_file: Optional[Path]) -> None:
        """Configure logger handlers and formatters."""
        self._logger.handlers.clear()
        level = self._get_log_level()
        self._logger.setLevel(level)

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(LogFormatter())
        self._logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(LogFormatter())
            self._logger.addHandler(file_handler)

    def _get_log_level(self) -> int:
        """Map verbosity to logging level."""
        mapping = {
            VerbosityLevel.QUIET: logging.ERROR,
            VerbosityLevel.NORMAL: logging.INFO,
            VerbosityLevel.VERBOSE: logging.DEBUG,
            VerbosityLevel.DEBUG: logging.DEBUG,
        }
        return mapping.get(self._verbosity, logging.INFO)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, kwargs)

    def _log(self, level: int, message: str, extra: Dict[str, Any]) -> None:
        """Internal logging method."""
        if extra:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            message = f"{message} [{extra_str}]"
        self._logger.log(level, message)

    def log_analysis_start(self, error_preview: str) -> None:
        """Log start of error analysis."""
        self.info(f"Starting error analysis: {error_preview[:100]}...")

    def log_analysis_complete(self, duration_ms: int, confidence: float) -> None:
        """Log completion of analysis."""
        self.info(
            "Analysis complete",
            duration_ms=duration_ms,
            confidence=f"{confidence:.0%}",
        )

    def log_solution_generation(self, count: int) -> None:
        """Log solution generation."""
        self.info(f"Generated {count} solution(s)")

    def log_llm_call(self, prompt_tokens: int, response_tokens: int) -> None:
        """Log LLM API call."""
        self.debug(
            "LLM call completed",
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
        )

    def log_exception(self, exception: Exception) -> None:
        """Log an exception."""
        self.error(f"Exception occurred: {type(exception).__name__}: {exception}")

    def log_git_operation(self, operation: str, path: str) -> None:
        """Log Git operation."""
        self.debug(f"Git operation: {operation}", path=path)

    def log_codebase_scan(self, files_scanned: int) -> None:
        """Log codebase scan progress."""
        self.info(f"Scanned {files_scanned} files")
