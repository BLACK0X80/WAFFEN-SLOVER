"""
Solution generation engine for Waffen-Solver.

Generates multiple solution options with trade-off analysis
using template method pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from waffen_solver.config.settings import WaffenSolverConfig
from waffen_solver.llm.provider import LLMProvider, GenerationConfig
from waffen_solver.llm.prompt_builder import PromptBuilder
from waffen_solver.llm.response_parser import ResponseParser
from waffen_solver.models.solution import (
    Solution,
    RankedSolution,
    TradeOffAnalysis,
    ComplexityLevel,
    RiskLevel,
)
from waffen_solver.models.context import AggregatedContext
from waffen_solver.models.analysis_result import ErrorAnalysis


class SolutionRankingEngine:
    """
    Ranks solutions based on multiple criteria.

    Provides scoring and ranking for generated solutions.
    """

    COMPLEXITY_WEIGHTS = {
        ComplexityLevel.LOW: 1.0,
        ComplexityLevel.MEDIUM: 0.7,
        ComplexityLevel.HIGH: 0.4,
        ComplexityLevel.VERY_HIGH: 0.2,
    }

    RISK_WEIGHTS = {
        RiskLevel.LOW: 1.0,
        RiskLevel.MEDIUM: 0.7,
        RiskLevel.HIGH: 0.4,
        RiskLevel.CRITICAL: 0.1,
    }

    def rank_solutions(self, solutions: List[Solution]) -> List[RankedSolution]:
        """
        Rank a list of solutions.

        Args:
            solutions: Solutions to rank.

        Returns:
            List of ranked solutions.
        """
        ranked = []
        for solution in solutions:
            score = self._calculate_score(solution)
            ranked.append(RankedSolution(
                solution=solution,
                rank_score=score,
                ranking_factors=self._get_ranking_factors(solution),
            ))

        ranked.sort(key=lambda x: x.rank_score, reverse=True)

        for i, ranked_solution in enumerate(ranked):
            ranked_solution.rank_position = i + 1

        return ranked

    def _calculate_score(self, solution: Solution) -> float:
        """Calculate ranking score for solution."""
        complexity_score = self.COMPLEXITY_WEIGHTS.get(solution.complexity, 0.5)
        risk_score = self.RISK_WEIGHTS.get(solution.risk_level, 0.5)
        pros_score = min(len(solution.pros) * 0.1, 0.3)
        cons_penalty = min(len(solution.cons) * 0.05, 0.2)

        score = (complexity_score * 0.3 + risk_score * 0.4 + pros_score - cons_penalty)
        return max(0.0, min(1.0, score))

    def _get_ranking_factors(self, solution: Solution) -> List[str]:
        """Get factors that influenced ranking."""
        factors = []

        if solution.complexity == ComplexityLevel.LOW:
            factors.append("Low implementation complexity")
        if solution.risk_level == RiskLevel.LOW:
            factors.append("Low risk level")
        if len(solution.pros) > len(solution.cons):
            factors.append("More advantages than disadvantages")

        return factors


class SolutionValidator:
    """Validates generated solutions."""

    def validate(self, solution: Solution) -> bool:
        """
        Validate a solution.

        Args:
            solution: Solution to validate.

        Returns:
            True if valid.
        """
        if not solution.title:
            return False
        if not solution.approach:
            return False
        return True

    def filter_valid(self, solutions: List[Solution]) -> List[Solution]:
        """Filter to only valid solutions."""
        return [s for s in solutions if self.validate(s)]


class SolutionGenerator:
    """
    Generates multiple solution options with trade-off analysis.

    Implements Template Method pattern for solution generation pipeline.

    Attributes:
        llm_provider: LLM provider for generation.
        ranking_engine: Solution ranking engine.
        validator: Solution validator.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        config: Optional[WaffenSolverConfig] = None,
    ) -> None:
        """
        Initialize solution generator.

        Args:
            llm_provider: LLM provider for generation.
            config: Optional configuration.
        """
        self._llm_provider = llm_provider
        self._config = config or WaffenSolverConfig()
        self._ranking_engine = SolutionRankingEngine()
        self._validator = SolutionValidator()
        self._prompt_builder = PromptBuilder()
        self._response_parser = ResponseParser()

    @property
    def ranking_engine(self) -> SolutionRankingEngine:
        """Get the ranking engine."""
        return self._ranking_engine

    @property
    def validator(self) -> SolutionValidator:
        """Get the validator."""
        return self._validator

    def generate_solutions(
        self,
        analysis: ErrorAnalysis,
        context: Optional[AggregatedContext] = None,
    ) -> List[Solution]:
        """
        Generate solutions for an error analysis.

        Args:
            analysis: Error analysis result.
            context: Optional context.

        Returns:
            List of generated solutions.
        """
        codebase_context = self._format_codebase_context(context)
        git_context = self._format_git_context(context)

        prompt = self._prompt_builder.build_solution_prompt(
            analysis,
            codebase_context,
            git_context,
        )

        gen_config = GenerationConfig(
            system_prompt=self._prompt_builder.get_system_prompt(),
        )

        response = self._llm_provider.generate(prompt, gen_config)
        solutions = self._response_parser.parse_solutions_response(response)

        return self._validator.filter_valid(solutions)

    def rank_solutions(self, solutions: List[Solution]) -> List[RankedSolution]:
        """
        Rank solutions by preference.

        Args:
            solutions: Solutions to rank.

        Returns:
            Ranked solutions.
        """
        return self._ranking_engine.rank_solutions(solutions)

    def evaluate_trade_offs(self, solution: Solution) -> TradeOffAnalysis:
        """
        Evaluate trade-offs for a solution.

        Args:
            solution: Solution to evaluate.

        Returns:
            Trade-off analysis.
        """
        notes = []

        if solution.complexity == ComplexityLevel.LOW:
            notes.append("Quick to implement but may need iteration")
        elif solution.complexity == ComplexityLevel.HIGH:
            notes.append("Comprehensive solution but requires significant effort")

        if solution.risk_level == RiskLevel.HIGH:
            notes.append("Higher risk - recommend thorough testing")

        return TradeOffAnalysis(
            performance_impact=self._assess_performance_impact(solution),
            maintainability_impact=self._assess_maintainability(solution),
            notes=notes,
        )

    def _format_codebase_context(self, context: Optional[AggregatedContext]) -> str:
        """Format codebase context for prompt."""
        if not context or not context.codebase:
            return ""

        parts = [
            f"Project: {context.codebase.project_type.value}",
            f"Architecture: {context.codebase.architecture.value}",
        ]

        if context.codebase.frameworks:
            parts.append(f"Frameworks: {', '.join(context.codebase.frameworks)}")

        return "\n".join(parts)

    def _format_git_context(self, context: Optional[AggregatedContext]) -> str:
        """Format Git context for prompt."""
        return ""

    def _assess_performance_impact(self, solution: Solution) -> str:
        """Assess performance impact."""
        if "performance" in solution.approach.lower():
            return "May affect performance - measure before/after"
        return "Minimal performance impact expected"

    def _assess_maintainability(self, solution: Solution) -> str:
        """Assess maintainability impact."""
        if solution.complexity in (ComplexityLevel.HIGH, ComplexityLevel.VERY_HIGH):
            return "Consider documenting the solution thoroughly"
        return "Should be easy to maintain"
