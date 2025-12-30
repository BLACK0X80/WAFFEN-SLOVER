"""Exceptions module for Waffen-Solver."""

from waffen_solver.exceptions.base import WaffenSolverException
from waffen_solver.exceptions.analysis_exceptions import (
    AnalysisException,
    ErrorParsingException,
    RootCauseNotFoundException,
    InsufficientContextException,
)
from waffen_solver.exceptions.git_exceptions import (
    GitException,
    RepositoryNotFoundException,
    InvalidRepositoryException,
    GitHistoryException,
)
from waffen_solver.exceptions.llm_exceptions import (
    LLMException,
    RateLimitException,
    InvalidResponseException,
    TokenLimitException,
)

__all__ = [
    "WaffenSolverException",
    "AnalysisException",
    "ErrorParsingException",
    "RootCauseNotFoundException",
    "InsufficientContextException",
    "GitException",
    "RepositoryNotFoundException",
    "InvalidRepositoryException",
    "GitHistoryException",
    "LLMException",
    "RateLimitException",
    "InvalidResponseException",
    "TokenLimitException",
]
