"""
Error analysis engine for Waffen-Solver.

Analyzes error messages and stack traces to identify
root causes using strategy pattern.
"""

import re
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type

from waffen_solver.config.settings import WaffenSolverConfig
from waffen_solver.exceptions import ErrorParsingException, InsufficientContextException
from waffen_solver.llm.provider import LLMProvider, GenerationConfig
from waffen_solver.llm.prompt_builder import PromptBuilder
from waffen_solver.llm.response_parser import ResponseParser
from waffen_solver.models.error import (
    Error,
    RawError,
    StackTrace,
    StackFrame,
    ErrorType,
    SeverityLevel,
)
from waffen_solver.models.context import AggregatedContext
from waffen_solver.models.analysis_result import ErrorAnalysis, RootCause, Factor


class AnalysisStrategy(ABC):
    """Abstract base class for analysis strategies."""

    @abstractmethod
    def can_handle(self, raw_error: RawError) -> bool:
        """Check if strategy can handle this error."""

    @abstractmethod
    def extract_info(self, raw_error: RawError) -> Dict[str, any]:
        """Extract error information."""


class PythonExceptionStrategy(AnalysisStrategy):
    """Strategy for Python exceptions."""

    EXCEPTION_PATTERN = re.compile(r"(\w+Error|\w+Exception):\s*(.+)", re.MULTILINE)

    def can_handle(self, raw_error: RawError) -> bool:
        """Check if this is a Python exception."""
        return bool(self.EXCEPTION_PATTERN.search(raw_error.message))

    def extract_info(self, raw_error: RawError) -> Dict[str, any]:
        """Extract Python exception information."""
        match = self.EXCEPTION_PATTERN.search(raw_error.message)
        if not match:
            return {}

        return {
            "exception_type": match.group(1),
            "message": match.group(2),
            "is_python": True,
        }


class GenericErrorStrategy(AnalysisStrategy):
    """Fallback strategy for generic errors."""

    def can_handle(self, raw_error: RawError) -> bool:
        """Always returns True as fallback."""
        return True

    def extract_info(self, raw_error: RawError) -> Dict[str, any]:
        """Extract basic error information."""
        return {
            "message": raw_error.message,
            "is_generic": True,
        }


class AnalysisStrategyFactory:
    """Factory for creating analysis strategies."""

    def __init__(self) -> None:
        """Initialize with default strategies."""
        self._strategies: List[AnalysisStrategy] = [
            PythonExceptionStrategy(),
            GenericErrorStrategy(),
        ]

    def get_strategy(self, raw_error: RawError) -> AnalysisStrategy:
        """Get appropriate strategy for error."""
        for strategy in self._strategies:
            if strategy.can_handle(raw_error):
                return strategy
        return self._strategies[-1]


class ErrorAnalyzer:
    """
    Analyzes error messages and stack traces.

    Uses Strategy pattern for different error types.

    Attributes:
        llm_provider: LLM provider for AI analysis.
        strategy_factory: Factory for analysis strategies.
    """

    ERROR_TYPE_MAPPING: Dict[str, ErrorType] = {
        "SyntaxError": ErrorType.SYNTAX,
        "TypeError": ErrorType.TYPE,
        "ValueError": ErrorType.VALUE,
        "NameError": ErrorType.NAME,
        "AttributeError": ErrorType.ATTRIBUTE,
        "IndexError": ErrorType.INDEX,
        "KeyError": ErrorType.KEY,
        "ImportError": ErrorType.IMPORT,
        "ModuleNotFoundError": ErrorType.IMPORT,
        "FileNotFoundError": ErrorType.IO,
        "IOError": ErrorType.IO,
        "MemoryError": ErrorType.MEMORY,
        "TimeoutError": ErrorType.TIMEOUT,
        "ConnectionError": ErrorType.NETWORK,
        "PermissionError": ErrorType.PERMISSION,
        "AssertionError": ErrorType.ASSERTION,
    }

    def __init__(
        self,
        llm_provider: LLMProvider,
        config: Optional[WaffenSolverConfig] = None,
    ) -> None:
        """
        Initialize error analyzer.

        Args:
            llm_provider: LLM provider for AI analysis.
            config: Optional configuration.
        """
        self._llm_provider = llm_provider
        self._config = config or WaffenSolverConfig()
        self._strategy_factory = AnalysisStrategyFactory()
        self._prompt_builder = PromptBuilder()
        self._response_parser = ResponseParser()

    def analyze(
        self,
        raw_error: RawError,
        context: Optional[AggregatedContext] = None,
    ) -> ErrorAnalysis:
        """
        Analyze an error.

        Args:
            raw_error: Raw error to analyze.
            context: Optional context.

        Returns:
            Error analysis result.
        """
        error = self._parse_error(raw_error)
        prompt = self._prompt_builder.build_analysis_prompt(error, context)

        gen_config = GenerationConfig(
            system_prompt=self._prompt_builder.get_system_prompt(),
        )

        response = self._llm_provider.generate(prompt, gen_config)
        return self._response_parser.parse_analysis_response(response)

    def identify_error_type(self, raw_error: RawError) -> ErrorType:
        """
        Identify error type from raw error.

        Args:
            raw_error: Raw error to classify.

        Returns:
            Identified error type.
        """
        for error_name, error_type in self.ERROR_TYPE_MAPPING.items():
            if error_name in raw_error.message:
                return error_type
        return ErrorType.UNKNOWN

    def extract_stack_trace(self, raw_error: RawError) -> Optional[StackTrace]:
        """
        Extract stack trace from raw error.

        Args:
            raw_error: Raw error with stack trace.

        Returns:
            Parsed stack trace or None.
        """
        if "Traceback" not in raw_error.message:
            return None

        frames = self._parse_traceback_frames(raw_error.message)
        return StackTrace(frames=frames, raw_trace=raw_error.message)

    def categorize_severity(self, error: Error) -> SeverityLevel:
        """
        Categorize error severity.

        Args:
            error: Error to categorize.

        Returns:
            Severity level.
        """
        critical_types = {ErrorType.MEMORY, ErrorType.PERMISSION, ErrorType.DATABASE}
        high_types = {ErrorType.SYNTAX, ErrorType.IMPORT, ErrorType.CONFIGURATION}

        if error.error_type in critical_types:
            return SeverityLevel.CRITICAL
        if error.error_type in high_types:
            return SeverityLevel.HIGH
        return SeverityLevel.MEDIUM

    def _parse_error(self, raw_error: RawError) -> Error:
        """Parse raw error into structured Error."""
        error_type = self.identify_error_type(raw_error)
        stack_trace = self.extract_stack_trace(raw_error)

        source_file = None
        line_number = None

        if stack_trace and stack_trace.frames:
            top_frame = stack_trace.get_top_frame()
            if top_frame:
                source_file = top_frame.file_path
                line_number = top_frame.line_number

        error = Error(
            raw_message=raw_error.message,
            error_type=error_type,
            stack_trace=stack_trace,
            source_file=source_file,
            line_number=line_number,
            timestamp=raw_error.timestamp,
        )

        error.severity = self.categorize_severity(error)
        return error

    def _parse_traceback_frames(self, trace_text: str) -> List[StackFrame]:
        """Parse traceback text into frames."""
        frame_pattern = re.compile(
            r'File "([^"]+)", line (\d+), in (\w+)'
        )

        frames = []
        for match in frame_pattern.finditer(trace_text):
            frame = StackFrame(
                file_path=Path(match.group(1)),
                line_number=int(match.group(2)),
                function_name=match.group(3),
            )
            frames.append(frame)

        return frames
