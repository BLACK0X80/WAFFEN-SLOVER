"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from waffen_solver.config.settings import WaffenSolverConfig, LLMConfig
from waffen_solver.models.error import RawError, Error, ErrorType, SeverityLevel
from waffen_solver.models.solution import Solution, ComplexityLevel, RiskLevel
from waffen_solver.models.context import CodebaseContext, ProjectType


@pytest.fixture
def mock_config() -> WaffenSolverConfig:
    """Create a mock configuration."""
    return WaffenSolverConfig()


@pytest.fixture
def mock_llm_config() -> LLMConfig:
    """Create a mock LLM configuration."""
    return LLMConfig(api_key="test-key")


@pytest.fixture
def sample_raw_error() -> RawError:
    """Create a sample raw error."""
    return RawError(
        message="""Traceback (most recent call last):
  File "main.py", line 10, in <module>
    result = calculate(x)
  File "calc.py", line 5, in calculate
    return x / 0
ZeroDivisionError: division by zero"""
    )


@pytest.fixture
def sample_error() -> Error:
    """Create a sample structured error."""
    return Error(
        raw_message="NameError: name 'x' is not defined",
        error_type=ErrorType.NAME,
        severity=SeverityLevel.MEDIUM,
        source_file=Path("test.py"),
        line_number=10,
    )


@pytest.fixture
def sample_solution() -> Solution:
    """Create a sample solution."""
    return Solution(
        title="Fix undefined variable",
        approach="Define the variable 'x' before using it",
        complexity=ComplexityLevel.LOW,
        risk_level=RiskLevel.LOW,
        pros=["Quick fix", "Low risk"],
        cons=["May need further investigation"],
    )


@pytest.fixture
def sample_codebase_context() -> CodebaseContext:
    """Create a sample codebase context."""
    return CodebaseContext(
        project_type=ProjectType.PYTHON_PACKAGE,
    )


@pytest.fixture
def mock_llm_provider() -> MagicMock:
    """Create a mock LLM provider."""
    mock = MagicMock()
    mock.generate.return_value = '{"error_type": "name", "severity": "medium", "root_cause": "Variable not defined"}'
    return mock


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    (project_dir / "main.py").write_text("print('hello')")
    (project_dir / "utils.py").write_text("def helper(): pass")

    src_dir = project_dir / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").write_text("")
    (src_dir / "module.py").write_text("class MyClass: pass")

    return project_dir
