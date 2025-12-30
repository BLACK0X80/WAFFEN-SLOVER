"""
Codebase scanning for Waffen-Solver.

Scans and indexes entire codebases with efficient
parallel scanning and caching.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
import fnmatch

from waffen_solver.models.context import (
    CodebaseContext,
    ProjectType,
    ArchitecturalStyle,
    DependencyInfo,
)


class FileFilter:
    """
    Filter for file inclusion/exclusion.

    Attributes:
        include_patterns: Patterns to include.
        exclude_patterns: Patterns to exclude.
    """

    DEFAULT_EXCLUDES = [
        "__pycache__",
        ".git",
        ".svn",
        "node_modules",
        ".venv",
        "venv",
        "*.pyc",
        "*.pyo",
        "*.so",
        "*.dll",
        ".idea",
        ".vscode",
    ]

    def __init__(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> None:
        """Initialize file filter."""
        self.include_patterns = include_patterns or ["*"]
        self.exclude_patterns = exclude_patterns or self.DEFAULT_EXCLUDES

    def should_include(self, path: Path) -> bool:
        """Check if path should be included."""
        path_str = str(path)

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return False
            if fnmatch.fnmatch(path_str, f"*/{pattern}/*"):
                return False
            if fnmatch.fnmatch(path_str, f"*/{pattern}"):
                return False

        for pattern in self.include_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True

        return False


class ScanCache:
    """
    Cache for scan results.

    Stores scanned file information.
    """

    def __init__(self) -> None:
        """Initialize scan cache."""
        self._files: Dict[str, dict] = {}
        self._structure: Optional[dict] = None

    def get_file(self, path: str) -> Optional[dict]:
        """Get cached file info."""
        return self._files.get(path)

    def set_file(self, path: str, info: dict) -> None:
        """Cache file info."""
        self._files[path] = info

    def get_structure(self) -> Optional[dict]:
        """Get cached structure."""
        return self._structure

    def set_structure(self, structure: dict) -> None:
        """Cache structure."""
        self._structure = structure


class ScanResult:
    """
    Result of a codebase scan.

    Attributes:
        root_path: Scanned root path.
        files: List of scanned files.
        directories: List of directories.
        file_count: Total file count.
    """

    def __init__(
        self,
        root_path: Path,
        files: List[Path],
        directories: List[Path],
    ) -> None:
        """Initialize scan result."""
        self.root_path = root_path
        self.files = files
        self.directories = directories
        self.file_count = len(files)


class ProjectStructure:
    """
    Project structure information.

    Attributes:
        root: Root directory.
        source_dirs: Source directories.
        test_dirs: Test directories.
        config_files: Configuration files.
    """

    def __init__(self) -> None:
        """Initialize project structure."""
        self.root: Optional[Path] = None
        self.source_dirs: List[Path] = []
        self.test_dirs: List[Path] = []
        self.config_files: List[Path] = []


class CodebaseScanner:
    """
    Scans and indexes the entire codebase.

    Implements efficient scanning with caching.

    Attributes:
        root_path: Root path to scan.
        file_filters: File filters.
        cache: Scan cache.
    """

    PROJECT_INDICATORS = {
        "pyproject.toml": ProjectType.PYTHON_PACKAGE,
        "setup.py": ProjectType.PYTHON_PACKAGE,
        "setup.cfg": ProjectType.PYTHON_PACKAGE,
        "package.json": ProjectType.WEB_APPLICATION,
        "requirements.txt": ProjectType.PYTHON_PACKAGE,
        "Pipfile": ProjectType.PYTHON_PACKAGE,
    }

    def __init__(
        self,
        root_path: Path,
        file_filter: Optional[FileFilter] = None,
        max_depth: int = 10,
    ) -> None:
        """
        Initialize codebase scanner.

        Args:
            root_path: Root path to scan.
            file_filter: Optional file filter.
            max_depth: Maximum scan depth.
        """
        self._root_path = Path(root_path)
        self._file_filter = file_filter or FileFilter()
        self._max_depth = max_depth
        self._cache = ScanCache()

    @property
    def root_path(self) -> Path:
        """Get root path."""
        return self._root_path

    @property
    def cache(self) -> ScanCache:
        """Get the cache."""
        return self._cache

    def scan(self) -> CodebaseContext:
        """
        Scan the codebase and return context.

        Returns:
            Codebase context.
        """
        scan_result = self.scan_directory(self._root_path)
        project_type = self.detect_project_type()
        dependencies = self.identify_dependencies()
        structure = self.map_structure()

        return CodebaseContext(
            project_type=project_type,
            architecture=ArchitecturalStyle.UNKNOWN,
            dependencies=dependencies,
            entry_points=structure.source_dirs,
        )

    def scan_directory(
        self,
        path: Path,
        current_depth: int = 0,
    ) -> ScanResult:
        """
        Scan a directory.

        Args:
            path: Directory to scan.
            current_depth: Current recursion depth.

        Returns:
            Scan result.
        """
        files: List[Path] = []
        directories: List[Path] = []

        if current_depth > self._max_depth:
            return ScanResult(path, files, directories)

        try:
            for item in path.iterdir():
                if not self._file_filter.should_include(item):
                    continue

                if item.is_file():
                    files.append(item)
                elif item.is_dir():
                    directories.append(item)
                    sub_result = self.scan_directory(item, current_depth + 1)
                    files.extend(sub_result.files)
                    directories.extend(sub_result.directories)
        except PermissionError:
            pass

        return ScanResult(path, files, directories)

    def detect_project_type(self) -> ProjectType:
        """
        Detect the project type.

        Returns:
            Detected project type.
        """
        for filename, project_type in self.PROJECT_INDICATORS.items():
            if (self._root_path / filename).exists():
                return project_type

        return ProjectType.UNKNOWN

    def identify_dependencies(self) -> List[DependencyInfo]:
        """
        Identify project dependencies.

        Returns:
            List of dependencies.
        """
        dependencies: List[DependencyInfo] = []

        requirements_path = self._root_path / "requirements.txt"
        if requirements_path.exists():
            dependencies.extend(self._parse_requirements(requirements_path))

        pyproject_path = self._root_path / "pyproject.toml"
        if pyproject_path.exists():
            dependencies.extend(self._parse_pyproject(pyproject_path))

        return dependencies

    def map_structure(self) -> ProjectStructure:
        """
        Map the project structure.

        Returns:
            Project structure information.
        """
        structure = ProjectStructure()
        structure.root = self._root_path

        src_candidates = ["src", "lib", "app"]
        for candidate in src_candidates:
            candidate_path = self._root_path / candidate
            if candidate_path.is_dir():
                structure.source_dirs.append(candidate_path)

        test_candidates = ["tests", "test", "spec"]
        for candidate in test_candidates:
            candidate_path = self._root_path / candidate
            if candidate_path.is_dir():
                structure.test_dirs.append(candidate_path)

        config_patterns = ["*.toml", "*.cfg", "*.ini", "*.yaml", "*.yml"]
        for pattern in config_patterns:
            structure.config_files.extend(self._root_path.glob(pattern))

        return structure

    def _parse_requirements(self, path: Path) -> List[DependencyInfo]:
        """Parse requirements.txt file."""
        dependencies: List[DependencyInfo] = []

        try:
            content = path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split("==")
                name = parts[0].split(">=")[0].split("<=")[0].strip()
                version = parts[1] if len(parts) > 1 else ""

                if name:
                    dependencies.append(DependencyInfo(name=name, version=version))
        except (OSError, UnicodeDecodeError):
            pass

        return dependencies

    def _parse_pyproject(self, path: Path) -> List[DependencyInfo]:
        """Parse pyproject.toml for dependencies."""
        dependencies: List[DependencyInfo] = []

        try:
            content = path.read_text(encoding="utf-8")
            if "[tool.poetry.dependencies]" in content:
                in_deps = False
                for line in content.splitlines():
                    if "[tool.poetry.dependencies]" in line:
                        in_deps = True
                        continue
                    if in_deps and line.startswith("["):
                        break
                    if in_deps and "=" in line:
                        parts = line.split("=")
                        name = parts[0].strip()
                        if name and name != "python":
                            dependencies.append(DependencyInfo(name=name))
        except (OSError, UnicodeDecodeError):
            pass

        return dependencies
