"""
Response parsing utilities for Waffen-Solver.

Parses LLM responses into structured data models
with validation and error handling.
"""

import json
import re
from typing import Any, Dict, List, Optional

from waffen_solver.exceptions import InvalidResponseException
from waffen_solver.models.error import ErrorType, SeverityLevel
from waffen_solver.models.solution import (
    Solution,
    CodeImplementation,
    ComplexityLevel,
    RiskLevel,
    TimeEstimate,
)
from waffen_solver.models.analysis_result import (
    ErrorAnalysis,
    RootCause,
    Factor,
)


class ResponseParser:
    """
    Parses LLM responses into structured data.

    Handles multiple output formats and validation.
    """

    def __init__(self) -> None:
        """Initialize response parser."""
        self._json_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")

    def parse_analysis_response(self, response: str) -> ErrorAnalysis:
        """
        Parse error analysis response.

        Args:
            response: LLM response string.

        Returns:
            Parsed ErrorAnalysis.

        Raises:
            InvalidResponseException: If parsing fails.
        """
        data = self._extract_json(response)

        error_type = self._parse_error_type(data.get("error_type", "unknown"))
        severity = self._parse_severity(data.get("severity", "medium"))

        root_cause = RootCause(
            description=data.get("root_cause", "Unknown root cause"),
            confidence=float(data.get("confidence", 0.5)),
        )

        factors = [
            Factor(description=f)
            for f in data.get("contributing_factors", [])
        ]

        return ErrorAnalysis(
            error_type=error_type,
            severity=severity,
            root_cause=root_cause,
            contributing_factors=factors,
            affected_components=data.get("affected_components", []),
            confidence=float(data.get("confidence", 0.5)),
        )

    def parse_solutions_response(self, response: str) -> List[Solution]:
        """
        Parse solutions response.

        Args:
            response: LLM response string.

        Returns:
            List of parsed Solutions.

        Raises:
            InvalidResponseException: If parsing fails.
        """
        data = self._extract_json(response)
        solutions_data = data.get("solutions", [])

        if not solutions_data:
            return []

        return [self._parse_single_solution(s) for s in solutions_data]

    def parse_explanation_response(self, response: str) -> str:
        """
        Parse explanation response.

        Args:
            response: LLM response string.

        Returns:
            Cleaned explanation text.
        """
        text = response.strip()
        text = re.sub(r"```[\s\S]*?```", "", text)
        return text.strip()

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from response."""
        match = self._json_pattern.search(response)
        if match:
            json_str = match.group(1)
        else:
            json_str = response

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return self._fuzzy_parse_json(json_str)

    def _fuzzy_parse_json(self, text: str) -> Dict[str, Any]:
        """Attempt fuzzy JSON parsing."""
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        raise InvalidResponseException(
            "Failed to parse JSON from response",
            response_preview=text[:200],
        )

    def _parse_error_type(self, value: str) -> ErrorType:
        """Parse error type from string."""
        value = value.lower().strip()
        for error_type in ErrorType:
            if error_type.value == value:
                return error_type
        return ErrorType.UNKNOWN

    def _parse_severity(self, value: str) -> SeverityLevel:
        """Parse severity from string."""
        value = value.lower().strip()
        for severity in SeverityLevel:
            if severity.value == value:
                return severity
        return SeverityLevel.MEDIUM

    def _parse_complexity(self, value: str) -> ComplexityLevel:
        """Parse complexity from string."""
        value = value.lower().strip()
        for complexity in ComplexityLevel:
            if complexity.value == value:
                return complexity
        return ComplexityLevel.MEDIUM

    def _parse_risk(self, value: str) -> RiskLevel:
        """Parse risk level from string."""
        value = value.lower().strip()
        for risk in RiskLevel:
            if risk.value == value:
                return risk
        return RiskLevel.MEDIUM

    def _parse_single_solution(self, data: Dict[str, Any]) -> Solution:
        """Parse a single solution from data."""
        implementation = CodeImplementation(
            code=data.get("implementation", ""),
            instructions=data.get("instructions", []),
        )

        time_estimate = TimeEstimate(
            description=data.get("time_estimate", ""),
        )

        return Solution(
            title=data.get("title", "Solution"),
            approach=data.get("approach", ""),
            implementation=implementation,
            pros=data.get("pros", []),
            cons=data.get("cons", []),
            complexity=self._parse_complexity(data.get("complexity", "medium")),
            risk_level=self._parse_risk(data.get("risk_level", "medium")),
            time_estimate=time_estimate,
            best_for=data.get("best_for", []),
        )
