"""
Git blame tracking for Waffen-Solver.

Tracks code authorship for context and expertise
identification (non-judgmental).
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

from waffen_solver.git.repository import GitRepository
from waffen_solver.models.git_info import Author, BlameInfo


class AuthorCache:
    """
    Cache for author information.

    Stores author data and expertise mapping.
    """

    def __init__(self) -> None:
        """Initialize author cache."""
        self._authors: Dict[str, Author] = {}
        self._expertise: Dict[str, Set[str]] = {}

    def get_author(self, email: str) -> Optional[Author]:
        """Get cached author by email."""
        return self._authors.get(email)

    def set_author(self, author: Author) -> None:
        """Cache an author."""
        self._authors[author.email] = author

    def add_expertise(self, email: str, area: str) -> None:
        """Add expertise area for author."""
        if email not in self._expertise:
            self._expertise[email] = set()
        self._expertise[email].add(area)

    def get_expertise(self, email: str) -> List[str]:
        """Get expertise areas for author."""
        return list(self._expertise.get(email, set()))


class CodeSection:
    """
    Represents a section of code.

    Attributes:
        file_path: Path to the file.
        start_line: Starting line.
        end_line: Ending line.
    """

    def __init__(
        self,
        file_path: Path,
        start_line: int,
        end_line: int,
    ) -> None:
        """Initialize code section."""
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line


class CollaborationGraph:
    """
    Graph of code collaboration patterns.

    Tracks which authors work together on files.
    """

    def __init__(self) -> None:
        """Initialize collaboration graph."""
        self._edges: Dict[str, Dict[str, int]] = {}

    def add_collaboration(self, author1_email: str, author2_email: str) -> None:
        """Record collaboration between two authors."""
        if author1_email not in self._edges:
            self._edges[author1_email] = {}
        if author2_email not in self._edges:
            self._edges[author2_email] = {}

        self._edges[author1_email][author2_email] = (
            self._edges[author1_email].get(author2_email, 0) + 1
        )
        self._edges[author2_email][author1_email] = (
            self._edges[author2_email].get(author1_email, 0) + 1
        )

    def get_collaborators(self, email: str) -> List[str]:
        """Get list of collaborators for an author."""
        if email not in self._edges:
            return []
        sorted_collabs = sorted(
            self._edges[email].items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [c for c, _ in sorted_collabs]


class BlameTracker:
    """
    Tracks code authorship for context.

    Provides insights about code ownership and expertise
    in a non-judgmental way.

    Attributes:
        repository: Git repository.
        author_cache: Author cache.
    """

    def __init__(self, repository: GitRepository) -> None:
        """
        Initialize blame tracker.

        Args:
            repository: Git repository to track.
        """
        self._repository = repository
        self._author_cache = AuthorCache()
        self._collaboration_graph = CollaborationGraph()

    @property
    def repository(self) -> GitRepository:
        """Get the repository."""
        return self._repository

    @property
    def author_cache(self) -> AuthorCache:
        """Get the author cache."""
        return self._author_cache

    def get_code_authors(
        self,
        file_path: Path,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> List[Author]:
        """
        Get authors of code in a file or range.

        Args:
            file_path: Path to the file.
            start_line: Optional starting line.
            end_line: Optional ending line.

        Returns:
            List of authors.
        """
        blame_info = self._repository.get_file_blame(file_path)

        if start_line is None and end_line is None:
            return list(set(blame_info.line_authors.values()))

        authors: Set[Author] = set()
        for line_num, author in blame_info.line_authors.items():
            if start_line and line_num < start_line:
                continue
            if end_line and line_num > end_line:
                continue
            authors.add(author)
            self._author_cache.set_author(author)

        return list(authors)

    def find_expertise_area(self, author: Author) -> List[str]:
        """
        Find expertise areas for an author.

        Args:
            author: Author to find expertise for.

        Returns:
            List of expertise areas.
        """
        cached = self._author_cache.get_expertise(author.email)
        if cached:
            return cached

        commits = self._repository.get_commit_history(limit=500)
        file_counts: Dict[str, int] = {}

        for commit in commits:
            if commit.author.email != author.email:
                continue
            for file_path in commit.files_changed:
                directory = str(Path(file_path).parent)
                file_counts[directory] = file_counts.get(directory, 0) + 1

        sorted_dirs = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        expertise = [d for d, _ in sorted_dirs[:5]]

        for area in expertise:
            self._author_cache.add_expertise(author.email, area)

        return expertise

    def identify_review_candidates(
        self,
        code_section: CodeSection,
    ) -> List[Author]:
        """
        Identify authors who could review code.

        Args:
            code_section: Code section to review.

        Returns:
            List of potential reviewers.
        """
        authors = self.get_code_authors(
            code_section.file_path,
            code_section.start_line,
            code_section.end_line,
        )

        related_files = self._repository.find_related_files(code_section.file_path)
        for related_file in related_files[:3]:
            related_authors = self.get_code_authors(related_file)
            for author in related_authors:
                if author not in authors:
                    authors.append(author)

        return authors[:5]

    def analyze_collaboration_patterns(self) -> CollaborationGraph:
        """
        Analyze collaboration patterns in repository.

        Returns:
            Collaboration graph.
        """
        commits = self._repository.get_commit_history(limit=200)

        file_authors: Dict[str, Set[str]] = {}
        for commit in commits:
            for file_path in commit.files_changed:
                if file_path not in file_authors:
                    file_authors[file_path] = set()
                file_authors[file_path].add(commit.author.email)

        for file_path, authors in file_authors.items():
            author_list = list(authors)
            for i, author1 in enumerate(author_list):
                for author2 in author_list[i + 1:]:
                    self._collaboration_graph.add_collaboration(author1, author2)

        return self._collaboration_graph
