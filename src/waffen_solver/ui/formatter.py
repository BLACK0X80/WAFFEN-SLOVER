"""
Output formatting for Waffen-Solver.

Formats output for terminal display with
multiple styles and language support.
"""

from typing import Any, Dict, List, Optional

from waffen_solver.config.settings import Language, OutputFormat
from waffen_solver.models.analysis_result import AnalysisResult
from waffen_solver.models.solution import Solution, RankedSolution
from waffen_solver.core.explainer import Explanation


class StyleConfig:
    """
    Configuration for output styling.

    Attributes:
        use_colors: Whether to use colors.
        use_bold: Whether to use bold text.
        show_details: Whether to show details.
    """

    def __init__(
        self,
        use_colors: bool = True,
        use_bold: bool = True,
        show_details: bool = True,
    ) -> None:
        """Initialize style config."""
        self.use_colors = use_colors
        self.use_bold = use_bold
        self.show_details = show_details


class FormattedOutput:
    """
    Formatted output ready for rendering.

    Attributes:
        sections: Output sections.
        format_type: Output format type.
    """

    def __init__(
        self,
        sections: List[Dict[str, Any]],
        format_type: str = "default",
    ) -> None:
        """Initialize formatted output."""
        self.sections = sections
        self.format_type = format_type


class LanguageFormatter:
    """
    Language-aware formatting.

    Handles RTL for Arabic and LTR for English.
    """

    def format_for_language(
        self,
        text: str,
        language: Language,
    ) -> str:
        """
        Format text for specific language.

        Args:
            text: Text to format.
            language: Target language.

        Returns:
            Formatted text.
        """
        if language == Language.ARABIC:
            return self._apply_rtl(text)
        return text

    def _apply_rtl(self, text: str) -> str:
        """Apply RTL formatting."""
        return text


class OutputFormatter:
    """
    Formats output for terminal display.

    Supports multiple output formats and styles.

    Attributes:
        style_config: Style configuration.
        language_formatter: Language formatter.
    """

    def __init__(
        self,
        style_config: Optional[StyleConfig] = None,
        output_format: OutputFormat = OutputFormat.RICH,
    ) -> None:
        """
        Initialize output formatter.

        Args:
            style_config: Style configuration.
            output_format: Output format.
        """
        self._style_config = style_config or StyleConfig()
        self._output_format = output_format
        self._language_formatter = LanguageFormatter()

    @property
    def style_config(self) -> StyleConfig:
        """Get style config."""
        return self._style_config

    @property
    def language_formatter(self) -> LanguageFormatter:
        """Get language formatter."""
        return self._language_formatter

    def format_analysis(
        self,
        analysis: AnalysisResult,
    ) -> FormattedOutput:
        """
        Format analysis result for display.

        Args:
            analysis: Analysis to format.

        Returns:
            Formatted output.
        """
        sections: List[Dict[str, Any]] = []

        sections.append({
            "type": "header",
            "title": "Error Analysis",
            "subtitle": analysis.error.error_type.value,
        })

        sections.append({
            "type": "panel",
            "title": "Root Cause",
            "content": analysis.root_cause.description,
            "style": "red",
        })

        sections.append({
            "type": "info",
            "items": [
                ("Severity", analysis.analysis.severity.value),
                ("Confidence", f"{analysis.confidence:.0%}"),
                ("Error Type", analysis.error.error_type.value),
            ],
        })

        if analysis.contributing_factors:
            sections.append({
                "type": "list",
                "title": "Contributing Factors",
                "items": [f.description for f in analysis.contributing_factors],
            })

        return FormattedOutput(sections, "analysis")

    def format_solutions(
        self,
        solutions: List[RankedSolution],
    ) -> FormattedOutput:
        """
        Format solutions for display.

        Args:
            solutions: Solutions to format.

        Returns:
            Formatted output.
        """
        sections: List[Dict[str, Any]] = []

        sections.append({
            "type": "header",
            "title": "Solutions",
            "subtitle": f"{len(solutions)} options generated",
        })

        for ranked in solutions:
            solution = ranked.solution
            sections.append({
                "type": "solution",
                "rank": ranked.rank_position,
                "score": ranked.rank_score,
                "title": solution.title,
                "approach": solution.approach,
                "complexity": solution.complexity.value,
                "risk": solution.risk_level.value,
                "pros": solution.pros,
                "cons": solution.cons,
            })

        return FormattedOutput(sections, "solutions")

    def format_explanation(
        self,
        explanation: Explanation,
    ) -> FormattedOutput:
        """
        Format explanation for display.

        Args:
            explanation: Explanation to format.

        Returns:
            Formatted output.
        """
        sections: List[Dict[str, Any]] = []

        sections.append({
            "type": "header",
            "title": "Explanation",
            "subtitle": f"{explanation.level.value} level",
        })

        sections.append({
            "type": "text",
            "content": explanation.content,
        })

        return FormattedOutput(sections, "explanation")

    def format_as_json(self, data: Any) -> str:
        """
        Format data as JSON string.

        Args:
            data: Data to format.

        Returns:
            JSON string.
        """
        import json
        if hasattr(data, "model_dump"):
            return json.dumps(data.model_dump(), indent=2, default=str)
        return json.dumps(data, indent=2, default=str)

    def format_as_plain(self, sections: List[Dict[str, Any]]) -> str:
        """
        Format sections as plain text.

        Args:
            sections: Sections to format.

        Returns:
            Plain text string.
        """
        lines: List[str] = []

        for section in sections:
            section_type = section.get("type", "")

            if section_type == "header":
                lines.append(f"\n=== {section['title']} ===")
                if section.get("subtitle"):
                    lines.append(f"    {section['subtitle']}")

            elif section_type == "panel":
                lines.append(f"\n{section['title']}:")
                lines.append(f"  {section['content']}")

            elif section_type == "info":
                for key, value in section.get("items", []):
                    lines.append(f"  {key}: {value}")

            elif section_type == "list":
                lines.append(f"\n{section.get('title', 'Items')}:")
                for item in section.get("items", []):
                    lines.append(f"  - {item}")

            elif section_type == "text":
                lines.append(section.get("content", ""))

        return "\n".join(lines)
