"""
Git information data models for Waffen-Solver.

Contains Pydantic models for representing Git-related
information including commits, changes, and blame.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Author(BaseModel):
    """
    Git author information.

    Attributes:
        name: Author name.
        email: Author email.
        username: Git username.
    """

    name: str
    email: str = ""
    username: str = ""


class Commit(BaseModel):
    """
    Git commit information.

    Attributes:
        sha: Commit hash.
        short_sha: Short commit hash.
        message: Commit message.
        author: Commit author.
        timestamp: Commit timestamp.
        files_changed: List of changed files.
        insertions: Lines inserted.
        deletions: Lines deleted.
    """

    sha: str
    short_sha: str = ""
    message: str
    author: Author
    timestamp: datetime
    files_changed: List[str] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0

    def __init__(self, **data: Any) -> None:
        """Initialize commit with short_sha derived from sha."""
        super().__init__(**data)
        if not self.short_sha and self.sha:
            self.short_sha = self.sha[:7]


class Change(BaseModel):
    """
    A file change in Git history.

    Attributes:
        file_path: Path to changed file.
        change_type: Type of change.
        commit: Associated commit.
        lines_added: Lines added.
        lines_removed: Lines removed.
    """

    file_path: Path
    change_type: str = "modified"
    commit: Optional[Commit] = None
    lines_added: int = 0
    lines_removed: int = 0


class BlameInfo(BaseModel):
    """
    Git blame information for a file.

    Attributes:
        file_path: Path to the file.
        line_authors: Mapping of line numbers to authors.
        line_commits: Mapping of line numbers to commits.
        last_modified: Last modification time.
    """

    file_path: Path
    line_authors: Dict[int, Author] = Field(default_factory=dict)
    line_commits: Dict[int, str] = Field(default_factory=dict)
    last_modified: Optional[datetime] = None

    def get_author_for_line(self, line: int) -> Optional[Author]:
        """Get author for a specific line."""
        return self.line_authors.get(line)

    def get_commit_for_line(self, line: int) -> Optional[str]:
        """Get commit SHA for a specific line."""
        return self.line_commits.get(line)


class FileHistory(BaseModel):
    """
    History of a file in Git.

    Attributes:
        file_path: Path to the file.
        commits: List of commits affecting file.
        total_changes: Total number of changes.
        first_commit: First commit adding file.
        last_commit: Most recent commit.
    """

    file_path: Path
    commits: List[Commit] = Field(default_factory=list)
    total_changes: int = 0
    first_commit: Optional[Commit] = None
    last_commit: Optional[Commit] = None


class FragileArea(BaseModel):
    """
    An area of code identified as fragile.

    Areas with high change frequency or many
    bug fixes are flagged as fragile.

    Attributes:
        file_path: Path to the file.
        start_line: Starting line.
        end_line: Ending line.
        change_count: Number of changes.
        bug_fix_count: Number of bug fixes.
        risk_score: Calculated risk score.
        last_changed: Last change timestamp.
    """

    file_path: Path
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    change_count: int = 0
    bug_fix_count: int = 0
    risk_score: float = Field(ge=0.0, le=1.0, default=0.5)
    last_changed: Optional[datetime] = None


class ChangePatterns(BaseModel):
    """
    Patterns detected in change history.

    Attributes:
        frequently_changed: Frequently changed files.
        co_changed: Files often changed together.
        hotspots: Code hotspots.
    """

    frequently_changed: List[Path] = Field(default_factory=list)
    co_changed: Dict[str, List[str]] = Field(default_factory=dict)
    hotspots: List[FragileArea] = Field(default_factory=list)


class DiffAnalysis(BaseModel):
    """
    Analysis of a Git diff.

    Attributes:
        commit: Associated commit.
        files_changed: Changed files.
        total_additions: Total line additions.
        total_deletions: Total line deletions.
        breaking_changes: Identified breaking changes.
        risk_assessment: Risk assessment.
    """

    commit: Optional[Commit] = None
    files_changed: List[Change] = Field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    breaking_changes: List[str] = Field(default_factory=list)
    risk_assessment: str = ""


class GitContext(BaseModel):
    """
    Context extracted from Git history.

    Comprehensive Git context for debugging.

    Attributes:
        recent_commits: Recent commits.
        related_changes: Changes related to error.
        file_history: History of relevant files.
        blame_info: Blame information.
        fragile_areas: Identified fragile areas.
        change_patterns: Change patterns.
        repository_path: Path to repository.
    """

    recent_commits: List[Commit] = Field(default_factory=list)
    related_changes: List[Change] = Field(default_factory=list)
    file_history: Optional[FileHistory] = None
    blame_info: Optional[BlameInfo] = None
    fragile_areas: List[FragileArea] = Field(default_factory=list)
    change_patterns: Optional[ChangePatterns] = None
    repository_path: Optional[Path] = None

    def has_recent_activity(self) -> bool:
        """Check if there is recent commit activity."""
        return len(self.recent_commits) > 0

    def get_recent_authors(self) -> List[Author]:
        """Get authors from recent commits."""
        return [commit.author for commit in self.recent_commits]
