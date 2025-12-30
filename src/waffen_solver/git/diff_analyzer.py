"""
Git diff analysis for Waffen-Solver.

Analyzes code differences for change impact
and risk assessment.
"""

from pathlib import Path
from typing import List, Optional
import re

from waffen_solver.git.repository import GitRepository
from waffen_solver.models.git_info import Commit, Change, DiffAnalysis


class SemanticAnalyzer:
    """
    Analyzes semantic meaning of code changes.

    Identifies breaking changes and high-risk modifications.
    """

    BREAKING_PATTERNS = [
        re.compile(r"\bdef\s+\w+\s*\([^)]*\)\s*:", re.MULTILINE),
        re.compile(r"\bclass\s+\w+", re.MULTILINE),
        re.compile(r"\bremove[ds]?\b", re.IGNORECASE),
        re.compile(r"\bdelete[ds]?\b", re.IGNORECASE),
        re.compile(r"\bdeprecate[ds]?\b", re.IGNORECASE),
    ]

    RISK_KEYWORDS = [
        "security",
        "auth",
        "password",
        "credential",
        "database",
        "production",
        "critical",
    ]

    def analyze_change_semantics(self, content: str) -> dict:
        """
        Analyze semantic content of a change.

        Args:
            content: Diff content.

        Returns:
            Analysis results.
        """
        is_breaking = any(p.search(content) for p in self.BREAKING_PATTERNS)

        content_lower = content.lower()
        risk_matches = [kw for kw in self.RISK_KEYWORDS if kw in content_lower]

        return {
            "is_breaking": is_breaking,
            "risk_keywords": risk_matches,
            "risk_level": "high" if risk_matches else "low",
        }

    def is_function_signature_change(self, content: str) -> bool:
        """Check if change modifies function signatures."""
        return bool(re.search(r"[-+]\s*def\s+\w+\s*\(", content))

    def is_class_change(self, content: str) -> bool:
        """Check if change modifies class definitions."""
        return bool(re.search(r"[-+]\s*class\s+\w+", content))


class RiskAssessment:
    """
    Risk assessment for code changes.

    Attributes:
        level: Risk level (low, medium, high, critical).
        factors: Factors contributing to risk.
        recommendations: Risk mitigation recommendations.
    """

    def __init__(
        self,
        level: str = "low",
        factors: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> None:
        """Initialize risk assessment."""
        self.level = level
        self.factors = factors or []
        self.recommendations = recommendations or []


class BreakingChange:
    """
    Represents a breaking change.

    Attributes:
        description: Change description.
        file_path: Affected file.
        line_range: Affected lines.
        impact: Impact description.
    """

    def __init__(
        self,
        description: str,
        file_path: Path,
        line_range: Optional[tuple[int, int]] = None,
        impact: str = "",
    ) -> None:
        """Initialize breaking change."""
        self.description = description
        self.file_path = file_path
        self.line_range = line_range
        self.impact = impact


class RelatedChange:
    """
    A change related to another change.

    Attributes:
        change: The related change.
        relationship: Type of relationship.
        confidence: Confidence in relationship.
    """

    def __init__(
        self,
        change: Change,
        relationship: str,
        confidence: float = 0.5,
    ) -> None:
        """Initialize related change."""
        self.change = change
        self.relationship = relationship
        self.confidence = confidence


class DiffAnalyzer:
    """
    Analyzes code differences for change impact.

    Implements sophisticated diff interpretation.

    Attributes:
        repository: Git repository.
        semantic_analyzer: Semantic analysis component.
    """

    def __init__(self, repository: GitRepository) -> None:
        """
        Initialize diff analyzer.

        Args:
            repository: Git repository.
        """
        self._repository = repository
        self._semantic_analyzer = SemanticAnalyzer()

    @property
    def repository(self) -> GitRepository:
        """Get the repository."""
        return self._repository

    @property
    def semantic_analyzer(self) -> SemanticAnalyzer:
        """Get the semantic analyzer."""
        return self._semantic_analyzer

    def analyze_commit_diff(self, commit: Commit) -> DiffAnalysis:
        """
        Analyze diff for a commit.

        Args:
            commit: Commit to analyze.

        Returns:
            Diff analysis.
        """
        changes: List[Change] = []
        breaking_changes: List[str] = []

        for file_path in commit.files_changed:
            change = Change(
                file_path=Path(file_path),
                commit=commit,
            )
            changes.append(change)

        risk = self.assess_change_risk(commit)

        return DiffAnalysis(
            commit=commit,
            files_changed=changes,
            breaking_changes=breaking_changes,
            risk_assessment=risk.level,
        )

    def identify_breaking_changes(
        self,
        commit: Commit,
    ) -> List[BreakingChange]:
        """
        Identify breaking changes in a commit.

        Args:
            commit: Commit to analyze.

        Returns:
            List of breaking changes.
        """
        breaking: List[BreakingChange] = []
        message_lower = commit.message.lower()

        if "breaking" in message_lower or "deprecate" in message_lower:
            for file_path in commit.files_changed:
                breaking.append(BreakingChange(
                    description=f"Potentially breaking change in {file_path}",
                    file_path=Path(file_path),
                ))

        return breaking

    def assess_change_risk(self, commit: Commit) -> RiskAssessment:
        """
        Assess risk level of a commit.

        Args:
            commit: Commit to assess.

        Returns:
            Risk assessment.
        """
        factors: List[str] = []
        recommendations: List[str] = []

        num_files = len(commit.files_changed)
        if num_files > 10:
            factors.append(f"Large change affecting {num_files} files")
            recommendations.append("Consider breaking into smaller changes")

        message_lower = commit.message.lower()
        for keyword in self._semantic_analyzer.RISK_KEYWORDS:
            if keyword in message_lower:
                factors.append(f"Contains sensitive keyword: {keyword}")

        level = "low"
        if len(factors) >= 2:
            level = "high"
        elif len(factors) == 1:
            level = "medium"

        return RiskAssessment(
            level=level,
            factors=factors,
            recommendations=recommendations,
        )

    def find_related_changes(
        self,
        change: Change,
        limit: int = 5,
    ) -> List[RelatedChange]:
        """
        Find changes related to a given change.

        Args:
            change: Change to find related for.
            limit: Maximum related changes.

        Returns:
            List of related changes.
        """
        related: List[RelatedChange] = []

        commits = self._repository.get_commit_history(
            change.file_path,
            limit=20,
        )

        for commit in commits:
            if change.commit and commit.sha == change.commit.sha:
                continue

            for file_path in commit.files_changed:
                if file_path != str(change.file_path):
                    related_change = Change(
                        file_path=Path(file_path),
                        commit=commit,
                    )
                    related.append(RelatedChange(
                        change=related_change,
                        relationship="co-changed",
                        confidence=0.7,
                    ))

        return related[:limit]
