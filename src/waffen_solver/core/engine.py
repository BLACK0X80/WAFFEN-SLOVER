"""
Main debugging engine for Waffen-Solver.

Orchestrates all components using Chain of Responsibility
pattern for complete debugging workflow.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import time

from waffen_solver.config.settings import WaffenSolverConfig, LLMConfig
from waffen_solver.core.analyzer import ErrorAnalyzer
from waffen_solver.core.solver import SolutionGenerator
from waffen_solver.core.explainer import ErrorExplainer, ExplanationLevel, Explanation
from waffen_solver.core.context_manager import ContextManager
from waffen_solver.llm.provider import ClaudeProvider
from waffen_solver.models.error import Error, RawError
from waffen_solver.models.solution import Solution, RankedSolution
from waffen_solver.models.context import AggregatedContext, CodebaseContext
from waffen_solver.models.analysis_result import AnalysisResult, ErrorAnalysis
from waffen_solver.models.git_info import GitContext
from waffen_solver.utils.logger import WaffenSolverLogger


class DebuggingEngine:
    """
    Main orchestrator for the debugging process.

    Coordinates all components using Chain of Responsibility pattern.

    Attributes:
        analyzer: Error analyzer component.
        solver: Solution generator component.
        explainer: Error explainer component.
        context_manager: Context management component.
    """

    def __init__(
        self,
        config: Optional[WaffenSolverConfig] = None,
    ) -> None:
        """
        Initialize debugging engine.

        Args:
            config: Optional configuration.
        """
        self._config = config or WaffenSolverConfig()
        self._logger = WaffenSolverLogger.get_instance(
            verbosity=self._config.verbosity,
        )
        self._llm_provider = ClaudeProvider(self._config.llm)
        self._analyzer = ErrorAnalyzer(self._llm_provider, self._config)
        self._solver = SolutionGenerator(self._llm_provider, self._config)
        self._explainer = ErrorExplainer(self._llm_provider, self._config)
        self._context_manager = ContextManager()

    @property
    def analyzer(self) -> ErrorAnalyzer:
        """Get the error analyzer."""
        return self._analyzer

    @property
    def solver(self) -> SolutionGenerator:
        """Get the solution generator."""
        return self._solver

    @property
    def explainer(self) -> ErrorExplainer:
        """Get the error explainer."""
        return self._explainer

    @property
    def context_manager(self) -> ContextManager:
        """Get the context manager."""
        return self._context_manager

    def analyze_error(
        self,
        error_input: str,
        context: Optional[AggregatedContext] = None,
    ) -> AnalysisResult:
        """
        Analyze an error and return structured analysis.

        Args:
            error_input: Raw error message/stack trace.
            context: Optional context.

        Returns:
            Complete analysis result.
        """
        start_time = time.time()
        self._logger.log_analysis_start(error_input)

        raw_error = RawError(message=error_input)
        ctx = context or self._context_manager.build_context()

        analysis = self._analyzer.analyze(raw_error, ctx)

        error = self._build_error_from_analysis(raw_error, analysis)
        self._context_manager.add_error_to_session(error)

        duration_ms = int((time.time() - start_time) * 1000)
        self._logger.log_analysis_complete(duration_ms, analysis.confidence)

        return AnalysisResult(
            error=error,
            analysis=analysis,
            root_cause=analysis.root_cause,
            contributing_factors=analysis.contributing_factors,
            context=ctx,
            confidence=analysis.confidence,
            analysis_duration_ms=duration_ms,
        )

    def generate_solutions(
        self,
        analysis: AnalysisResult,
    ) -> List[RankedSolution]:
        """
        Generate and rank solutions for an analysis.

        Args:
            analysis: Error analysis result.

        Returns:
            List of ranked solutions.
        """
        solutions = self._solver.generate_solutions(
            analysis.analysis,
            analysis.context,
        )

        self._logger.log_solution_generation(len(solutions))

        return self._solver.rank_solutions(solutions)

    def explain_error(
        self,
        error: Error,
        root_cause: str,
        level: ExplanationLevel = ExplanationLevel.SIMPLE,
    ) -> Explanation:
        """
        Generate explanation for an error.

        Args:
            error: Error to explain.
            root_cause: Root cause description.
            level: Explanation detail level.

        Returns:
            Generated explanation.
        """
        return self._explainer.explain(
            error,
            root_cause,
            level,
            self._config.language.default,
        )

    def debug(
        self,
        error_input: str,
    ) -> dict:
        """
        Complete debugging workflow.

        Analyzes error, generates solutions, and creates explanations.

        Args:
            error_input: Raw error message.

        Returns:
            Dictionary with analysis, solutions, and explanation.
        """
        analysis = self.analyze_error(error_input)
        solutions = self.generate_solutions(analysis)

        explanation = self.explain_error(
            analysis.error,
            analysis.root_cause.description,
        )

        return {
            "analysis": analysis,
            "solutions": solutions,
            "explanation": explanation,
        }

    def learn_from_codebase(self, path: Path) -> CodebaseContext:
        """
        Learn context from a codebase.

        Args:
            path: Path to codebase.

        Returns:
            Learned codebase context.
        """
        from waffen_solver.codebase.scanner import CodebaseScanner

        scanner = CodebaseScanner(path)
        context = scanner.scan()

        self._context_manager.set_codebase_context(context)
        return context

    def integrate_git_history(self, repo_path: Path) -> GitContext:
        """
        Integrate Git history for debugging insights.

        Args:
            repo_path: Path to Git repository.

        Returns:
            Git context.
        """
        from waffen_solver.git.repository import GitRepository
        from waffen_solver.git.history_analyzer import HistoryAnalyzer

        repo = GitRepository(repo_path)
        analyzer = HistoryAnalyzer(repo)

        return analyzer.build_context()

    def _build_error_from_analysis(
        self,
        raw_error: RawError,
        analysis: ErrorAnalysis,
    ) -> Error:
        """Build Error model from raw error and analysis."""
        return Error(
            raw_message=raw_error.message,
            error_type=analysis.error_type,
            severity=analysis.severity,
            timestamp=raw_error.timestamp,
        )
