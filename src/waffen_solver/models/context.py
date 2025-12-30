"""
Context data models for Waffen-Solver.

Contains Pydantic models for representing various
types of context used in error analysis.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContextSource(str, Enum):
    """Sources of context information."""

    CODEBASE = "codebase"
    GIT = "git"
    SESSION = "session"
    ENVIRONMENT = "environment"
    USER_INPUT = "user_input"
    FILE_SYSTEM = "file_system"


class ProjectType(str, Enum):
    """Types of projects."""

    PYTHON_PACKAGE = "python_package"
    WEB_APPLICATION = "web_application"
    API_SERVICE = "api_service"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    MONOREPO = "monorepo"
    UNKNOWN = "unknown"


class ArchitecturalStyle(str, Enum):
    """Architectural styles."""

    MVC = "mvc"
    LAYERED = "layered"
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    EVENT_DRIVEN = "event_driven"
    HEXAGONAL = "hexagonal"
    CLEAN = "clean"
    UNKNOWN = "unknown"


class DetectedPattern(BaseModel):
    """
    A detected design pattern in the codebase.

    Attributes:
        name: Pattern name.
        locations: Files where pattern is used.
        confidence: Detection confidence.
    """

    name: str
    locations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class CodingConventions(BaseModel):
    """
    Detected coding conventions.

    Attributes:
        naming_style: Naming convention style.
        docstring_style: Docstring format.
        import_style: Import organization style.
        max_line_length: Detected max line length.
    """

    naming_style: str = ""
    docstring_style: str = ""
    import_style: str = ""
    max_line_length: Optional[int] = None


class ModuleInfo(BaseModel):
    """
    Information about a module.

    Attributes:
        name: Module name.
        path: Module path.
        imports: Module imports.
        exports: Module exports.
    """

    name: str
    path: Path
    imports: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)


class DependencyInfo(BaseModel):
    """
    Dependency information.

    Attributes:
        name: Dependency name.
        version: Version string.
        is_dev: Whether it's a dev dependency.
    """

    name: str
    version: str = ""
    is_dev: bool = False


class CodebaseContext(BaseModel):
    """
    Learned context from codebase analysis.

    Contains comprehensive information about the
    analyzed codebase structure and patterns.

    Attributes:
        project_type: Type of project.
        architecture: Architectural style.
        frameworks: Detected frameworks.
        design_patterns: Detected patterns.
        coding_conventions: Coding conventions.
        modules: Module information.
        dependencies: Project dependencies.
        entry_points: Entry point files.
    """

    project_type: ProjectType = ProjectType.UNKNOWN
    architecture: ArchitecturalStyle = ArchitecturalStyle.UNKNOWN
    frameworks: List[str] = Field(default_factory=list)
    design_patterns: List[DetectedPattern] = Field(default_factory=list)
    coding_conventions: CodingConventions = Field(default_factory=CodingConventions)
    modules: List[ModuleInfo] = Field(default_factory=list)
    dependencies: List[DependencyInfo] = Field(default_factory=list)
    entry_points: List[Path] = Field(default_factory=list)


class SessionContext(BaseModel):
    """
    Context from the current debugging session.

    Attributes:
        session_id: Unique session identifier.
        start_time: Session start time.
        previous_errors: Previous errors in session.
        user_inputs: User inputs during session.
        analysis_history: Previous analyses.
    """

    session_id: str = ""
    start_time: datetime = Field(default_factory=datetime.now)
    previous_errors: List[str] = Field(default_factory=list)
    user_inputs: List[str] = Field(default_factory=list)
    analysis_history: List[Dict[str, Any]] = Field(default_factory=list)


class EnvironmentContext(BaseModel):
    """
    Environment context information.

    Attributes:
        python_version: Python version.
        os_info: Operating system info.
        virtual_env: Virtual environment path.
        installed_packages: Installed packages.
        environment_variables: Relevant env vars.
    """

    python_version: str = ""
    os_info: str = ""
    virtual_env: Optional[Path] = None
    installed_packages: Dict[str, str] = Field(default_factory=dict)
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class Context(BaseModel):
    """
    Base context model.

    Attributes:
        source: Source of this context.
        timestamp: When context was gathered.
        data: Context data.
    """

    source: ContextSource
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)


class AggregatedContext(BaseModel):
    """
    Aggregated context from multiple sources.

    Combines all available context types into
    a unified context object for analysis.

    Attributes:
        codebase: Codebase context.
        session: Session context.
        environment: Environment context.
        custom_contexts: Additional custom contexts.
        relevance_scores: Relevance scores by source.
    """

    codebase: Optional[CodebaseContext] = None
    session: Optional[SessionContext] = None
    environment: Optional[EnvironmentContext] = None
    custom_contexts: List[Context] = Field(default_factory=list)
    relevance_scores: Dict[str, float] = Field(default_factory=dict)

    def has_codebase_context(self) -> bool:
        """Check if codebase context is available."""
        return self.codebase is not None

    def has_session_context(self) -> bool:
        """Check if session context is available."""
        return self.session is not None

    def get_context_sources(self) -> List[ContextSource]:
        """Get list of available context sources."""
        sources: List[ContextSource] = []
        if self.codebase:
            sources.append(ContextSource.CODEBASE)
        if self.session:
            sources.append(ContextSource.SESSION)
        if self.environment:
            sources.append(ContextSource.ENVIRONMENT)
        for ctx in self.custom_contexts:
            sources.append(ctx.source)
        return sources
