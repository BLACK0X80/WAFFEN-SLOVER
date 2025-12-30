"""
Solution data models for Waffen-Solver.

Contains Pydantic models for representing solutions,
trade-off analysis, and implementation details.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ComplexityLevel(str, Enum):
    """Implementation complexity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskLevel(str, Enum):
    """Risk levels for solutions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeEstimate(BaseModel):
    """
    Time estimate for implementing a solution.

    Attributes:
        min_minutes: Minimum estimated minutes.
        max_minutes: Maximum estimated minutes.
        description: Human-readable time description.
    """

    min_minutes: int = 0
    max_minutes: int = 0
    description: str = ""

    def get_formatted(self) -> str:
        """Get formatted time estimate string."""
        if self.description:
            return self.description
        if self.min_minutes == self.max_minutes:
            return f"{self.min_minutes} minutes"
        return f"{self.min_minutes}-{self.max_minutes} minutes"


class CodeImplementation(BaseModel):
    """
    Code implementation details for a solution.

    Attributes:
        language: Programming language.
        code: The implementation code.
        file_path: Target file path if applicable.
        line_range: Line range to modify if applicable.
        instructions: Step-by-step instructions.
    """

    language: str = "python"
    code: str = ""
    file_path: Optional[str] = None
    line_range: Optional[tuple[int, int]] = None
    instructions: List[str] = Field(default_factory=list)


class TradeOffAnalysis(BaseModel):
    """
    Analysis of trade-offs for a solution.

    Attributes:
        performance_impact: Impact on performance.
        maintainability_impact: Impact on maintainability.
        scalability_impact: Impact on scalability.
        security_impact: Impact on security.
        notes: Additional notes.
    """

    performance_impact: str = ""
    maintainability_impact: str = ""
    scalability_impact: str = ""
    security_impact: str = ""
    notes: List[str] = Field(default_factory=list)


class TestStrategy(BaseModel):
    """
    Testing strategy for a solution.

    Attributes:
        unit_tests: Suggested unit tests.
        integration_tests: Suggested integration tests.
        manual_tests: Manual testing steps.
        edge_cases: Edge cases to test.
    """

    unit_tests: List[str] = Field(default_factory=list)
    integration_tests: List[str] = Field(default_factory=list)
    manual_tests: List[str] = Field(default_factory=list)
    edge_cases: List[str] = Field(default_factory=list)


class Solution(BaseModel):
    """
    Proposed solution with full analysis.

    Complete representation of a solution option
    with implementation details and trade-offs.

    Attributes:
        title: Solution title.
        approach: Approach description.
        implementation: Code implementation details.
        pros: Advantages of this solution.
        cons: Disadvantages of this solution.
        complexity: Implementation complexity.
        risk_level: Risk level.
        time_estimate: Time estimate.
        best_for: Use cases this is best for.
        test_strategy: Testing strategy.
        trade_offs: Trade-off analysis.
    """

    title: str
    approach: str
    implementation: CodeImplementation = Field(default_factory=CodeImplementation)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM
    risk_level: RiskLevel = RiskLevel.MEDIUM
    time_estimate: TimeEstimate = Field(default_factory=TimeEstimate)
    best_for: List[str] = Field(default_factory=list)
    test_strategy: TestStrategy = Field(default_factory=TestStrategy)
    trade_offs: Optional[TradeOffAnalysis] = None


class RankedSolution(BaseModel):
    """
    Solution with ranking score.

    Extends Solution with a ranking score for
    ordering solutions by preference.

    Attributes:
        solution: The solution being ranked.
        rank_score: Score from 0.0 to 1.0.
        rank_position: Position in ranking.
        ranking_factors: Factors that influenced ranking.
    """

    solution: Solution
    rank_score: float = Field(ge=0.0, le=1.0)
    rank_position: int = 1
    ranking_factors: List[str] = Field(default_factory=list)
