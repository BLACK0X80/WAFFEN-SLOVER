"""
Git repository wrapper for Waffen-Solver.

Provides high-level interface for Git operations
using GitPython.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from waffen_solver.exceptions import RepositoryNotFoundException, InvalidRepositoryException
from waffen_solver.models.git_info import Commit, Author, Change, BlameInfo, DiffAnalysis


class GitCache:
    """
    Cache for Git operations.

    Stores results of expensive Git operations.
    """

    def __init__(self) -> None:
        """Initialize cache."""
        self._commit_cache: Dict[str, Commit] = {}
        self._blame_cache: Dict[str, BlameInfo] = {}

    def get_commit(self, sha: str) -> Optional[Commit]:
        """Get cached commit."""
        return self._commit_cache.get(sha)

    def set_commit(self, sha: str, commit: Commit) -> None:
        """Cache a commit."""
        self._commit_cache[sha] = commit

    def get_blame(self, file_path: str) -> Optional[BlameInfo]:
        """Get cached blame info."""
        return self._blame_cache.get(file_path)

    def set_blame(self, file_path: str, blame: BlameInfo) -> None:
        """Cache blame info."""
        self._blame_cache[file_path] = blame

    def clear(self) -> None:
        """Clear all caches."""
        self._commit_cache.clear()
        self._blame_cache.clear()


class GitRepository:
    """
    Wrapper around GitPython for repository operations.

    Provides high-level interface for Git operations.

    Attributes:
        repo: GitPython Repo object.
        cache: Git operation cache.
    """

    def __init__(self, path: Path) -> None:
        """
        Initialize Git repository wrapper.

        Args:
            path: Path to repository.

        Raises:
            RepositoryNotFoundException: If path doesn't exist.
            InvalidRepositoryException: If not a valid Git repo.
        """
        self._path = path
        self._cache = GitCache()
        self._repo = self._open_repository(path)

    @property
    def repo(self) -> git.Repo:
        """Get the GitPython Repo object."""
        return self._repo

    @property
    def cache(self) -> GitCache:
        """Get the cache."""
        return self._cache

    @property
    def path(self) -> Path:
        """Get repository path."""
        return self._path

    def _open_repository(self, path: Path) -> git.Repo:
        """Open Git repository."""
        try:
            return git.Repo(path)
        except NoSuchPathError as exc:
            raise RepositoryNotFoundException(path) from exc
        except InvalidGitRepositoryError as exc:
            raise InvalidRepositoryException(path, "Not a valid Git repository") from exc

    def get_commit_history(
        self,
        file_path: Optional[Path] = None,
        limit: int = 100,
    ) -> List[Commit]:
        """
        Get commit history.

        Args:
            file_path: Optional file to get history for.
            limit: Maximum commits to return.

        Returns:
            List of commits.
        """
        commits = []
        kwargs = {"max_count": limit}

        if file_path:
            kwargs["paths"] = str(file_path)

        for git_commit in self._repo.iter_commits(**kwargs):
            commit = self._convert_commit(git_commit)
            commits.append(commit)

        return commits

    def get_file_blame(self, file_path: Path) -> BlameInfo:
        """
        Get blame information for a file.

        Args:
            file_path: Path to file.

        Returns:
            Blame information.
        """
        cached = self._cache.get_blame(str(file_path))
        if cached:
            return cached

        line_authors: Dict[int, Author] = {}
        line_commits: Dict[int, str] = {}

        try:
            for blame_entry in self._repo.blame("HEAD", str(file_path)):
                commit, lines = blame_entry
                author = Author(
                    name=commit.author.name,
                    email=commit.author.email,
                )
                for i, _ in enumerate(lines):
                    line_num = i + 1
                    line_authors[line_num] = author
                    line_commits[line_num] = commit.hexsha
        except git.GitCommandError:
            pass

        blame_info = BlameInfo(
            file_path=file_path,
            line_authors=line_authors,
            line_commits=line_commits,
        )

        self._cache.set_blame(str(file_path), blame_info)
        return blame_info

    def get_recent_changes(
        self,
        since: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[Change]:
        """
        Get recent changes.

        Args:
            since: Get changes since this time.
            limit: Maximum changes to return.

        Returns:
            List of changes.
        """
        changes: List[Change] = []
        commits = self.get_commit_history(limit=limit)

        for commit in commits:
            if since and commit.timestamp < since:
                break

            for file_path in commit.files_changed:
                change = Change(
                    file_path=Path(file_path),
                    commit=commit,
                )
                changes.append(change)

        return changes

    def analyze_diff(self, commit_a: str, commit_b: str) -> DiffAnalysis:
        """
        Analyze diff between two commits.

        Args:
            commit_a: First commit SHA.
            commit_b: Second commit SHA.

        Returns:
            Diff analysis.
        """
        commit_obj_a = self._repo.commit(commit_a)
        commit_obj_b = self._repo.commit(commit_b)

        diffs = commit_obj_a.diff(commit_obj_b)

        changes: List[Change] = []
        total_additions = 0
        total_deletions = 0

        for diff in diffs:
            change_type = "modified"
            if diff.new_file:
                change_type = "added"
            elif diff.deleted_file:
                change_type = "deleted"

            change = Change(
                file_path=Path(diff.a_path or diff.b_path),
                change_type=change_type,
            )
            changes.append(change)

        return DiffAnalysis(
            files_changed=changes,
            total_additions=total_additions,
            total_deletions=total_deletions,
        )

    def find_related_files(self, file_path: Path) -> List[Path]:
        """
        Find files related to a given file.

        Args:
            file_path: File to find related files for.

        Returns:
            List of related file paths.
        """
        related: List[Path] = []
        commits = self.get_commit_history(file_path, limit=20)

        file_counts: Dict[str, int] = {}
        for commit in commits:
            for changed_file in commit.files_changed:
                if changed_file != str(file_path):
                    file_counts[changed_file] = file_counts.get(changed_file, 0) + 1

        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        for file_str, _ in sorted_files[:10]:
            related.append(Path(file_str))

        return related

    def _convert_commit(self, git_commit: git.Commit) -> Commit:
        """Convert GitPython commit to our model."""
        cached = self._cache.get_commit(git_commit.hexsha)
        if cached:
            return cached

        author = Author(
            name=git_commit.author.name,
            email=git_commit.author.email,
        )

        files_changed = []
        try:
            if git_commit.parents:
                diffs = git_commit.diff(git_commit.parents[0])
                files_changed = [d.a_path or d.b_path for d in diffs]
        except git.GitCommandError:
            pass

        commit = Commit(
            sha=git_commit.hexsha,
            message=git_commit.message.strip(),
            author=author,
            timestamp=datetime.fromtimestamp(git_commit.committed_date),
            files_changed=files_changed,
        )

        self._cache.set_commit(git_commit.hexsha, commit)
        return commit
