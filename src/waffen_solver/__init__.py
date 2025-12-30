"""
Waffen-Solver: Enterprise-grade AI debugging assistant.

An intelligent debugging tool that combines AI analysis with
codebase understanding and Git history insights.
"""

__version__ = "0.1.0"

from waffen_solver.core.engine import DebuggingEngine
from waffen_solver.core.analyzer import ErrorAnalyzer
from waffen_solver.core.solver import SolutionGenerator
from waffen_solver.core.explainer import ErrorExplainer
from waffen_solver.core.context_manager import ContextManager
from waffen_solver.config.settings import WaffenSolverConfig

__all__ = [
    "DebuggingEngine",
    "ErrorAnalyzer",
    "SolutionGenerator",
    "ErrorExplainer",
    "ContextManager",
    "WaffenSolverConfig",
    "__version__",
]
