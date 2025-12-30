"""
Prompt building utilities for Waffen-Solver.

Provides optimized prompt construction with
template management and context optimization.
"""

from typing import Any, Dict, Optional

from waffen_solver.config.prompts import PromptTemplates
from waffen_solver.models.error import Error
from waffen_solver.models.context import AggregatedContext
from waffen_solver.models.analysis_result import ErrorAnalysis


class ContextOptimizer:
    """
    Optimizes context for prompt inclusion.

    Reduces context size while preserving relevance.
    """

    def __init__(self, max_tokens: int = 4000) -> None:
        """Initialize with maximum token budget."""
        self._max_tokens = max_tokens

    def optimize(self, context: AggregatedContext) -> str:
        """
        Optimize context to fit within token budget.

        Args:
            context: Full context to optimize.

        Returns:
            Optimized context string.
        """
        context_parts = []

        if context.codebase:
            context_parts.append(self._format_codebase_context(context.codebase))

        if context.environment:
            context_parts.append(self._format_environment_context(context.environment))

        full_context = "\n\n".join(context_parts)
        return self._truncate_to_tokens(full_context)

    def _format_codebase_context(self, codebase: Any) -> str:
        """Format codebase context."""
        parts = [
            f"Project Type: {codebase.project_type.value}",
            f"Architecture: {codebase.architecture.value}",
        ]
        if codebase.frameworks:
            parts.append(f"Frameworks: {', '.join(codebase.frameworks)}")
        return "\n".join(parts)

    def _format_environment_context(self, env: Any) -> str:
        """Format environment context."""
        parts = []
        if env.python_version:
            parts.append(f"Python: {env.python_version}")
        if env.os_info:
            parts.append(f"OS: {env.os_info}")
        return "\n".join(parts)

    def _truncate_to_tokens(self, text: str) -> str:
        """Truncate text to approximate token limit."""
        char_limit = self._max_tokens * 4
        if len(text) <= char_limit:
            return text
        return text[:char_limit] + "\n[Context truncated...]"


class PromptBuilder:
    """
    Builds optimized prompts for different tasks.

    Uses template pattern with variable substitution.

    Attributes:
        templates: Prompt template library.
        optimizer: Context optimizer.
    """

    def __init__(
        self,
        max_context_tokens: int = 4000,
    ) -> None:
        """
        Initialize prompt builder.

        Args:
            max_context_tokens: Maximum tokens for context.
        """
        self._templates = PromptTemplates
        self._optimizer = ContextOptimizer(max_context_tokens)

    def build_analysis_prompt(
        self,
        error: Error,
        context: Optional[AggregatedContext] = None,
    ) -> str:
        """
        Build prompt for error analysis.

        Args:
            error: Error to analyze.
            context: Optional context.

        Returns:
            Formatted analysis prompt.
        """
        stack_trace = ""
        if error.stack_trace and error.stack_trace.raw_trace:
            stack_trace = error.stack_trace.raw_trace

        context_str = ""
        if context:
            context_str = self._optimizer.optimize(context)

        return self._templates.format_template(
            "ERROR_ANALYSIS_TEMPLATE",
            error_message=error.raw_message,
            stack_trace=stack_trace or "No stack trace available",
            context=context_str or "No additional context available",
        )

    def build_solution_prompt(
        self,
        analysis: ErrorAnalysis,
        codebase_context: str = "",
        git_context: str = "",
    ) -> str:
        """
        Build prompt for solution generation.

        Args:
            analysis: Error analysis result.
            codebase_context: Codebase context string.
            git_context: Git context string.

        Returns:
            Formatted solution prompt.
        """
        analysis_str = self._format_analysis(analysis)

        return self._templates.format_template(
            "SOLUTION_GENERATION_TEMPLATE",
            analysis=analysis_str,
            codebase_context=codebase_context or "No codebase context available",
            git_context=git_context or "No Git context available",
        )

    def build_explanation_prompt(
        self,
        error: Error,
        root_cause: str,
        level: str = "simple",
        context: str = "",
        stack_trace: str = "",
    ) -> str:
        """
        Build prompt for error explanation.

        Args:
            error: Error to explain.
            root_cause: Identified root cause.
            level: Explanation level.
            context: Additional context.
            stack_trace: Stack trace string.

        Returns:
            Formatted explanation prompt.
        """
        template_map = {
            "simple": "SIMPLE_EXPLANATION_TEMPLATE",
            "technical": "TECHNICAL_EXPLANATION_TEMPLATE",
            "deep_dive": "DEEP_DIVE_EXPLANATION_TEMPLATE",
        }

        template_name = template_map.get(level, "SIMPLE_EXPLANATION_TEMPLATE")

        kwargs: Dict[str, str] = {
            "error_message": error.raw_message,
            "root_cause": root_cause,
        }

        if "context" in self._templates.get_template(template_name):
            kwargs["context"] = context or "No additional context"

        if "stack_trace" in self._templates.get_template(template_name):
            kwargs["stack_trace"] = stack_trace or "No stack trace available"

        return self._templates.format_template(template_name, **kwargs)

    def build_translation_prompt(
        self,
        content: str,
        target_language: str,
    ) -> str:
        """
        Build prompt for translation.

        Args:
            content: Content to translate.
            target_language: Target language.

        Returns:
            Formatted translation prompt.
        """
        return self._templates.format_template(
            "TRANSLATION_TEMPLATE",
            content=content,
            target_language=target_language,
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self._templates.SYSTEM_PROMPT

    def _format_analysis(self, analysis: ErrorAnalysis) -> str:
        """Format analysis for prompt inclusion."""
        lines = [
            f"Error Type: {analysis.error_type.value}",
            f"Severity: {analysis.severity.value}",
            f"Root Cause: {analysis.root_cause.description}",
            f"Confidence: {analysis.confidence:.0%}",
        ]

        if analysis.contributing_factors:
            factors = [f.description for f in analysis.contributing_factors]
            lines.append(f"Contributing Factors: {', '.join(factors)}")

        if analysis.affected_components:
            lines.append(f"Affected Components: {', '.join(analysis.affected_components)}")

        return "\n".join(lines)
