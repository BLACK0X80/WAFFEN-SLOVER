"""
File handling utilities for Waffen-Solver.

Provides safe file operations with path validation
and proper error handling.
"""

from pathlib import Path
from typing import List, Optional

from waffen_solver.exceptions import WaffenSolverException


class FileHandlerException(WaffenSolverException):
    """Exception raised for file handling errors."""

    def __init__(self, message: str, path: Optional[Path] = None) -> None:
        """Initialize with optional path context."""
        details = {"path": str(path)} if path else {}
        super().__init__(message, "FILE_HANDLER_ERROR", details)


class FileHandler:
    """
    Handles file operations safely.

    Provides methods for reading, writing, and validating
    file paths with proper error handling.

    Attributes:
        base_path: Base path for relative operations.
        allowed_extensions: Allowed file extensions.
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        allowed_extensions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize FileHandler.

        Args:
            base_path: Base path for relative operations.
            allowed_extensions: List of allowed file extensions.
        """
        self._base_path = base_path or Path.cwd()
        self._allowed_extensions = allowed_extensions or []

    @property
    def base_path(self) -> Path:
        """Get the base path."""
        return self._base_path

    def validate_path(self, path: Path) -> bool:
        """
        Validate a file path.

        Args:
            path: Path to validate.

        Returns:
            True if path is valid.

        Raises:
            FileHandlerException: If path is invalid.
        """
        resolved = self._resolve_path(path)
        if not self._is_safe_path(resolved):
            raise FileHandlerException(f"Path is outside allowed directory: {path}", path)
        if self._allowed_extensions:
            if resolved.suffix not in self._allowed_extensions:
                raise FileHandlerException(
                    f"File extension not allowed: {resolved.suffix}", path
                )
        return True

    def read_file(self, path: Path) -> str:
        """
        Read file contents safely.

        Args:
            path: Path to file.

        Returns:
            File contents as string.

        Raises:
            FileHandlerException: If file cannot be read.
        """
        resolved = self._resolve_path(path)
        self.validate_path(resolved)
        try:
            return resolved.read_text(encoding="utf-8")
        except OSError as exc:
            raise FileHandlerException(f"Failed to read file: {exc}", path) from exc

    def read_file_lines(self, path: Path) -> List[str]:
        """
        Read file as list of lines.

        Args:
            path: Path to file.

        Returns:
            List of lines.
        """
        content = self.read_file(path)
        return content.splitlines()

    def write_file(self, path: Path, content: str) -> None:
        """
        Write content to file safely.

        Args:
            path: Path to file.
            content: Content to write.

        Raises:
            FileHandlerException: If file cannot be written.
        """
        resolved = self._resolve_path(path)
        self.validate_path(resolved)
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise FileHandlerException(f"Failed to write file: {exc}", path) from exc

    def file_exists(self, path: Path) -> bool:
        """
        Check if file exists.

        Args:
            path: Path to check.

        Returns:
            True if file exists.
        """
        resolved = self._resolve_path(path)
        return resolved.is_file()

    def list_files(
        self,
        directory: Path,
        pattern: str = "*",
        recursive: bool = False,
    ) -> List[Path]:
        """
        List files in directory.

        Args:
            directory: Directory to list.
            pattern: Glob pattern.
            recursive: Whether to search recursively.

        Returns:
            List of file paths.
        """
        resolved = self._resolve_path(directory)
        if not resolved.is_dir():
            return []
        if recursive:
            return list(resolved.rglob(pattern))
        return list(resolved.glob(pattern))

    def _resolve_path(self, path: Path) -> Path:
        """Resolve path relative to base path."""
        if path.is_absolute():
            return path.resolve()
        return (self._base_path / path).resolve()

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within allowed directory."""
        try:
            path.resolve().relative_to(self._base_path.resolve())
            return True
        except ValueError:
            return path.is_absolute()
