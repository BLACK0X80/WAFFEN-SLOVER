"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from pathlib import Path

from waffen_solver.models.error import (
    Error,
    RawError,
    StackTrace,
    StackFrame,
    ErrorType,
    SeverityLevel,
)
from waffen_solver.models.solution import (
    Solution,
    RankedSolution,
    CodeImplementation,
    ComplexityLevel,
    RiskLevel,
    TimeEstimate,
)
from waffen_solver.models.context import (
    CodebaseContext,
    ProjectType,
    ArchitecturalStyle,
    AggregatedContext,
    ContextSource,
)


class TestErrorModels:
    """Tests for error models."""

    def test_raw_error_creation(self) -> None:
        """Test RawError creation."""
        error = RawError(message="Test error")
        assert error.message == "Test error"
        assert isinstance(error.timestamp, datetime)

    def test_stack_frame(self) -> None:
        """Test StackFrame creation."""
        frame = StackFrame(
            file_path=Path("test.py"),
            line_number=10,
            function_name="test_func",
        )
        assert frame.line_number == 10
        assert frame.function_name == "test_func"

    def test_stack_trace(self) -> None:
        """Test StackTrace creation."""
        frames = [
            StackFrame(file_path=Path("a.py"), line_number=1, function_name="a"),
            StackFrame(file_path=Path("b.py"), line_number=2, function_name="b"),
        ]
        trace = StackTrace(frames=frames)
        assert trace.get_top_frame().function_name == "a"
        assert trace.get_bottom_frame().function_name == "b"

    def test_error_creation(self) -> None:
        """Test Error creation."""
        error = Error(
            raw_message="NameError: name 'x' is not defined",
            error_type=ErrorType.NAME,
            severity=SeverityLevel.MEDIUM,
        )
        assert error.error_type == ErrorType.NAME
        assert error.severity == SeverityLevel.MEDIUM

    def test_error_location(self) -> None:
        """Test error location string."""
        error = Error(
            raw_message="Error",
            source_file=Path("test.py"),
            line_number=42,
        )
        assert error.get_error_location() == "test.py:42"


class TestSolutionModels:
    """Tests for solution models."""

    def test_time_estimate(self) -> None:
        """Test TimeEstimate formatting."""
        estimate = TimeEstimate(min_minutes=5, max_minutes=10)
        assert estimate.get_formatted() == "5-10 minutes"

    def test_time_estimate_single(self) -> None:
        """Test TimeEstimate with same min/max."""
        estimate = TimeEstimate(min_minutes=5, max_minutes=5)
        assert estimate.get_formatted() == "5 minutes"

    def test_solution_creation(self) -> None:
        """Test Solution creation."""
        solution = Solution(
            title="Fix the bug",
            approach="Change the variable name",
            complexity=ComplexityLevel.LOW,
            risk_level=RiskLevel.LOW,
        )
        assert solution.title == "Fix the bug"
        assert solution.complexity == ComplexityLevel.LOW

    def test_ranked_solution(self) -> None:
        """Test RankedSolution creation."""
        solution = Solution(title="Test", approach="Approach")
        ranked = RankedSolution(
            solution=solution,
            rank_score=0.85,
            rank_position=1,
        )
        assert ranked.rank_score == 0.85
        assert ranked.rank_position == 1


class TestContextModels:
    """Tests for context models."""

    def test_codebase_context(self) -> None:
        """Test CodebaseContext creation."""
        context = CodebaseContext(
            project_type=ProjectType.PYTHON_PACKAGE,
            architecture=ArchitecturalStyle.LAYERED,
        )
        assert context.project_type == ProjectType.PYTHON_PACKAGE

    def test_aggregated_context(self) -> None:
        """Test AggregatedContext methods."""
        context = AggregatedContext()
        assert not context.has_codebase_context()
        assert context.get_context_sources() == []

        context.codebase = CodebaseContext()
        assert context.has_codebase_context()
        assert ContextSource.CODEBASE in context.get_context_sources()
