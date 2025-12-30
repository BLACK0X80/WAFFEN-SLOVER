"""
Git history analysis for Waffen-Solver.

Analyzes Git history for debugging insights using
statistical analysis and pattern matching.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re

from waffen_solver.git.repository import GitRepository
from waffen_solver.models.git_info import (
    Commit,
    FragileArea,
    FileHistory,
    GitContext,
    ChangePatterns,
)
from waffen_solver.models.error import Error


class StatisticsEngine:
    """
    Statistical analysis for Git history.

    Provides statistical methods for analyzing
    commit patterns and change frequencies.
    """

    def calculate_change_frequency(self, commits: List[Commit]) -> float:
        """
        Calculate average changes per day.

        Args:
            commits: List of commits to analyze.

        Returns:
            Average changes per day.
        """
        if not commits or len(commits) < 2:
            return 0.0

        first = min(c.timestamp for c in commits)
        last = max(c.timestamp for c in commits)
        days = max((last - first).days, 1)

        return len(commits) / days

    def identify_hotspots(
        self,
        file_changes: Dict[str, int],
        threshold: int = 10,
    ) -> List[str]:
        """
        Identify code hotspots.

        Args:
            file_changes: Map of file to change count.
            threshold: Minimum changes for hotspot.

        Returns:
            List of hotspot file paths.
        """
        return [f for f, count in file_changes.items() if count >= threshold]


class PatternMatcher:
    """
    Pattern matching for commit messages.

    Identifies patterns in commits like bug fixes,
    feature additions, and refactoring.
    """

    BUG_FIX_PATTERNS = [
        re.compile(r"\bfix(es|ed)?\b", re.IGNORECASE),
        re.compile(r"\bbug\b", re.IGNORECASE),
        re.compile(r"\bresolve[ds]?\b", re.IGNORECASE),
        re.compile(r"\bpatch\b", re.IGNORECASE),
    ]

    def is_bug_fix(self, commit: Commit) -> bool:
        """Check if commit is a bug fix."""
        for pattern in self.BUG_FIX_PATTERNS:
            if pattern.search(commit.message):
                return True
        return False

    def categorize_commit(self, commit: Commit) -> str:
        """Categorize a commit by type."""
        if self.is_bug_fix(commit):
            return "bug_fix"
        if "feat" in commit.message.lower() or "add" in commit.message.lower():
            return "feature"
        if "refactor" in commit.message.lower():
            return "refactor"
        return "other"


class HistoryAnalyzer:
    """
    Analyzes Git history for debugging insights.

    Uses statistical analysis and pattern matching.

    Attributes:
        repository: Git repository wrapper.
        pattern_matcher: Pattern matcher.
        statistics_engine: Statistics engine.
    """

    def __init__(
        self,
        repository: GitRepository,
    ) -> None:
        """
        Initialize history analyzer.

        Args:
            repository: Git repository to analyze.
        """
        self._repository = repository
        self._pattern_matcher = PatternMatcher()
        self._statistics_engine = StatisticsEngine()

    @property
    def repository(self) -> GitRepository:
        """Get the repository."""
        return self._repository

    @property
    def pattern_matcher(self) -> PatternMatcher:
        """Get the pattern matcher."""
        return self._pattern_matcher

    @property
    def statistics_engine(self) -> StatisticsEngine:
        """Get the statistics engine."""
        return self._statistics_engine

    def find_introducing_commit(
        self,
        error: Error,
        file_path: Optional[Path] = None,
    ) -> Optional[Commit]:
        """
        Find commit that might have introduced an error.

        Args:
            error: Error to investigate.
            file_path: File related to error.

        Returns:
            Possibly introducing commit or None.
        """
        target_path = file_path or error.source_file
        if not target_path:
            return None

        commits = self._repository.get_commit_history(target_path, limit=20)
        if not commits:
            return None

        return commits[0]

    def analyze_change_frequency(self, file_path: Path) -> float:
        """
        Analyze change frequency for a file.

        Args:
            file_path: File to analyze.

        Returns:
            Change frequency (changes per day).
        """
        commits = self._repository.get_commit_history(file_path, limit=100)
        return self._statistics_engine.calculate_change_frequency(commits)

    def identify_fragile_areas(self) -> List[FragileArea]:
        """
        Identify fragile areas in the codebase.

        Returns:
            List of fragile areas.
        """
        commits = self._repository.get_commit_history(limit=500)

        file_changes: Dict[str, int] = {}
        file_bug_fixes: Dict[str, int] = {}

        for commit in commits:
            is_bug_fix = self._pattern_matcher.is_bug_fix(commit)
            for file_path in commit.files_changed:
                file_changes[file_path] = file_changes.get(file_path, 0) + 1
                if is_bug_fix:
                    file_bug_fixes[file_path] = file_bug_fixes.get(file_path, 0) + 1

        fragile_areas: List[FragileArea] = []

        for file_path, change_count in file_changes.items():
            bug_count = file_bug_fixes.get(file_path, 0)
            risk_score = self._calculate_risk_score(change_count, bug_count)

            if risk_score > 0.3:
                fragile_areas.append(FragileArea(
                    file_path=Path(file_path),
                    change_count=change_count,
                    bug_fix_count=bug_count,
                    risk_score=risk_score,
                ))

        fragile_areas.sort(key=lambda x: x.risk_score, reverse=True)
        return fragile_areas[:20]

    def find_similar_past_fixes(
        self,
        error: Error,
        limit: int = 5,
    ) -> List[Commit]:
        """
        Find commits that fixed similar issues.

        Args:
            error: Error to find fixes for.
            limit: Maximum fixes to return.

        Returns:
            List of relevant fix commits.
        """
        error_keywords = self._extract_keywords(error.raw_message)
        commits = self._repository.get_commit_history(limit=200)

        relevant_fixes: List[tuple[Commit, int]] = []

        for commit in commits:
            if not self._pattern_matcher.is_bug_fix(commit):
                continue

            score = self._score_relevance(commit.message, error_keywords)
            if score > 0:
                relevant_fixes.append((commit, score))

        relevant_fixes.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in relevant_fixes[:limit]]

    def build_context(self) -> GitContext:
        """
        Build complete Git context.

        Returns:
            Git context for debugging.
        """
        recent_commits = self._repository.get_commit_history(limit=20)
        fragile_areas = self.identify_fragile_areas()
        change_patterns = self._build_change_patterns()

        return GitContext(
            recent_commits=recent_commits,
            fragile_areas=fragile_areas,
            change_patterns=change_patterns,
            repository_path=self._repository.path,
        )

    def _calculate_risk_score(self, changes: int, bug_fixes: int) -> float:
        """Calculate risk score for a file."""
        if changes == 0:
            return 0.0

        bug_ratio = bug_fixes / changes
        change_factor = min(changes / 50, 1.0)

        score = (bug_ratio * 0.6) + (change_factor * 0.4)
        return min(score, 1.0)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from error text."""
        words = re.findall(r"\b\w+\b", text.lower())
        stopwords = {"the", "a", "an", "is", "was", "are", "in", "on", "at"}
        return [w for w in words if len(w) > 3 and w not in stopwords]

    def _score_relevance(self, message: str, keywords: List[str]) -> int:
        """Score relevance of commit message to keywords."""
        message_lower = message.lower()
        return sum(1 for kw in keywords if kw in message_lower)

    def _build_change_patterns(self) -> ChangePatterns:
        """Build change patterns from history."""
        commits = self._repository.get_commit_history(limit=100)

        file_changes: Dict[str, int] = {}
        for commit in commits:
            for file_path in commit.files_changed:
                file_changes[file_path] = file_changes.get(file_path, 0) + 1

        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
        frequently_changed = [Path(f) for f, _ in sorted_files[:10]]

        return ChangePatterns(frequently_changed=frequently_changed)
