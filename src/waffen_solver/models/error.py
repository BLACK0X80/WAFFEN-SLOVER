"""
Error data models for Waffen-Solver.

Contains Pydantic models for representing errors,
stack traces, and related error information.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Classification of error types."""

    SYNTAX = "syntax"
    RUNTIME = "runtime"
    TYPE = "type"
    VALUE = "value"
    NAME = "name"
    ATTRIBUTE = "attribute"
    INDEX = "index"
    KEY = "key"
    IMPORT = "import"
    IO = "io"
    MEMORY = "memory"
    TIMEOUT = "timeout"
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    ASSERTION = "assertion"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    """Severity levels for errors."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class StackFrame(BaseModel):
    """
    Represents a single frame in a stack trace.

    Attributes:
        file_path: Path to the source file.
        line_number: Line number in the file.
        function_name: Name of the function or method.
        code_context: The actual code at this frame.
        local_vars: Local variables if available.
    """

    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    code_context: Optional[str] = None
    local_vars: Dict[str, Any] = Field(default_factory=dict)


class StackTrace(BaseModel):
    """
    Represents a complete stack trace.

    Attributes:
        frames: List of stack frames from innermost to outermost.
        raw_trace: Original raw stack trace string.
    """

    frames: List[StackFrame] = Field(default_factory=list)
    raw_trace: Optional[str] = None

    def get_top_frame(self) -> Optional[StackFrame]:
        """Get the topmost (innermost) stack frame."""
        return self.frames[0] if self.frames else None

    def get_bottom_frame(self) -> Optional[StackFrame]:
        """Get the bottommost (outermost) stack frame."""
        return self.frames[-1] if self.frames else None


class EnvironmentInfo(BaseModel):
    """
    Environment information where error occurred.

    Attributes:
        python_version: Python version string.
        os_name: Operating system name.
        os_version: Operating system version.
        packages: Relevant package versions.
        env_vars: Relevant environment variables.
    """

    python_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    packages: Dict[str, str] = Field(default_factory=dict)
    env_vars: Dict[str, str] = Field(default_factory=dict)


class RawError(BaseModel):
    """
    Raw unprocessed error input.

    Attributes:
        message: The raw error message or output.
        source: Where the error came from.
        timestamp: When the error was captured.
    """

    message: str
    source: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class Error(BaseModel):
    """
    Structured representation of an error.

    Fully parsed and categorized error with all
    extracted information.

    Attributes:
        raw_message: Original error message.
        error_type: Classified error type.
        stack_trace: Parsed stack trace if available.
        source_file: File where error occurred.
        line_number: Line number of error.
        severity: Error severity level.
        timestamp: When error occurred.
        environment: Environment information.
        metadata: Additional metadata.
    """

    raw_message: str
    error_type: ErrorType = ErrorType.UNKNOWN
    stack_trace: Optional[StackTrace] = None
    source_file: Optional[Path] = None
    line_number: Optional[int] = None
    severity: SeverityLevel = SeverityLevel.MEDIUM
    timestamp: datetime = Field(default_factory=datetime.now)
    environment: Optional[EnvironmentInfo] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_error_location(self) -> str:
        """Get formatted error location string."""
        if self.source_file and self.line_number:
            return f"{self.source_file}:{self.line_number}"
        if self.source_file:
            return str(self.source_file)
        return "unknown location"

    def has_stack_trace(self) -> bool:
        """Check if error has a stack trace."""
        return self.stack_trace is not None and len(self.stack_trace.frames) > 0
