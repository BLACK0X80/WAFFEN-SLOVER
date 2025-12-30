"""
Analysis result data models for Waffen-Solver.

Contains Pydantic models for representing error analysis
results, root causes, and related information.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from waffen_solver.models.error import Error, ErrorType, SeverityLevel
from waffen_solver.models.context import AggregatedContext


class RootCause(BaseModel):
    """
    Identified root cause of an error.

    Attributes:
        description: Root cause description.
        category: Category of the cause.
        confidence: Confidence in this determination.
        evidence: Evidence supporting this cause.
        related_code: Code related to the cause.
    """

    description: str
    category: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence: List[str] = Field(default_factory=list)
    related_code: Optional[str] = None


class Factor(BaseModel):
    """
    Contributing factor to an error.

    Attributes:
        description: Factor description.
        impact: Impact level of this factor.
        is_primary: Whether this is a primary factor.
    """

    description: str
    impact: str = "medium"
    is_primary: bool = False


class CodeSegment(BaseModel):
    """
    A segment of code related to an error.

    Attributes:
        file_path: File containing the code.
        start_line: Starting line number.
        end_line: Ending line number.
        content: The code content.
        relevance: Relevance to the error.
    """

    file_path: Path
    start_line: int
    end_line: int
    content: str
    relevance: str = ""


class PastIssue(BaseModel):
    """
    A past issue similar to the current error.

    Attributes:
        error_message: The past error message.
        solution: How it was resolved.
        similarity: Similarity score.
        source: Where this was found.
    """

    error_message: str
    solution: str = ""
    similarity: float = Field(ge=0.0, le=1.0, default=0.5)
    source: str = ""


class ErrorAnalysis(BaseModel):
    """
    Analysis of a parsed error.

    Intermediate representation of error analysis
    before full result compilation.

    Attributes:
        error_type: Classified error type.
        severity: Error severity.
        root_cause: Identified root cause.
        contributing_factors: Contributing factors.
        affected_components: Affected components.
        confidence: Analysis confidence.
    """

    error_type: ErrorType
    severity: SeverityLevel
    root_cause: RootCause
    contributing_factors: List[Factor] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class AnalysisResult(BaseModel):
    """
    Complete analysis of an error.

    Contains all information from error analysis
    including context and related issues.

    Attributes:
        error: The analyzed error.
        analysis: Error analysis details.
        root_cause: Identified root cause.
        contributing_factors: Contributing factors.
        context: Aggregated context used.
        related_code: Related code segments.
        similar_past_issues: Similar past issues.
        confidence: Overall confidence.
        timestamp: When analysis was performed.
        analysis_duration_ms: Analysis duration.
    """

    error: Error
    analysis: ErrorAnalysis
    root_cause: RootCause
    contributing_factors: List[Factor] = Field(default_factory=list)
    context: Optional[AggregatedContext] = None
    related_code: List[CodeSegment] = Field(default_factory=list)
    similar_past_issues: List[PastIssue] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    timestamp: datetime = Field(default_factory=datetime.now)
    analysis_duration_ms: int = 0

    def get_summary(self) -> str:
        """Get a brief summary of the analysis."""
        return (
            f"Error: {self.error.error_type.value} | "
            f"Severity: {self.analysis.severity.value} | "
            f"Confidence: {self.confidence:.0%}"
        )

    def to_summary_dict(self) -> Dict[str, Any]:
        """Get summary as dictionary."""
        return {
            "error_type": self.error.error_type.value,
            "severity": self.analysis.severity.value,
            "root_cause": self.root_cause.description,
            "confidence": self.confidence,
            "factor_count": len(self.contributing_factors),
        }
