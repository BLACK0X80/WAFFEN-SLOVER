"""
Configuration settings for Waffen-Solver.

Uses Pydantic BaseSettings for environment-based configuration
with validation and type safety.
"""

from enum import Enum
from pathlib import Path
from typing import List

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Language(str, Enum):
    """Supported languages for the application."""

    ENGLISH = "en"
    ARABIC = "ar"


class OutputFormat(str, Enum):
    """Output format options."""

    RICH = "rich"
    PLAIN = "plain"
    JSON = "json"


class VerbosityLevel(str, Enum):
    """Verbosity level options."""

    QUIET = "quiet"
    NORMAL = "normal"
    VERBOSE = "verbose"
    DEBUG = "debug"


class LLMConfig(BaseSettings):
    """
    Configuration for LLM provider settings.

    Attributes:
        provider: The LLM provider to use (e.g., 'anthropic').
        api_key: Secret API key for the LLM service.
        model: Model identifier to use.
        max_tokens: Maximum tokens for generation.
        temperature: Sampling temperature.
    """

    model_config = SettingsConfigDict(
        env_prefix="WAFFEN_LLM_",
        extra="ignore",
    )

    provider: str = Field(default="anthropic")
    api_key: SecretStr = Field(default=SecretStr(""))
    model: str = Field(default="claude-sonnet-4-20250514")
    max_tokens: int = Field(default=4096, ge=1, le=100000)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)


class GitConfig(BaseSettings):
    """
    Configuration for Git integration.

    Attributes:
        enabled: Whether Git analysis is enabled.
        history_limit: Maximum commits to analyze.
        include_blame: Whether to include blame information.
    """

    model_config = SettingsConfigDict(
        env_prefix="WAFFEN_GIT_",
        extra="ignore",
    )

    enabled: bool = Field(default=True)
    history_limit: int = Field(default=100, ge=1, le=10000)
    include_blame: bool = Field(default=True)


class CodebaseConfig(BaseSettings):
    """
    Configuration for codebase scanning.

    Attributes:
        enabled: Whether codebase scanning is enabled.
        max_depth: Maximum directory depth to scan.
        excluded_patterns: Glob patterns to exclude.
        max_file_size: Maximum file size in bytes to process.
    """

    model_config = SettingsConfigDict(
        env_prefix="WAFFEN_CODEBASE_",
        extra="ignore",
    )

    enabled: bool = Field(default=True)
    max_depth: int = Field(default=10, ge=1, le=50)
    excluded_patterns: List[str] = Field(
        default_factory=lambda: [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "*.pyc",
            "*.pyo",
        ]
    )
    max_file_size: int = Field(default=1_000_000)


class LanguageConfig(BaseSettings):
    """
    Configuration for language handling.

    Attributes:
        default: Default language for output.
        translation_enabled: Whether translation is enabled.
        auto_detect: Whether to auto-detect input language.
    """

    model_config = SettingsConfigDict(
        env_prefix="WAFFEN_LANG_",
        extra="ignore",
    )

    default: Language = Field(default=Language.ENGLISH)
    translation_enabled: bool = Field(default=True)
    auto_detect: bool = Field(default=True)


class CacheConfig(BaseSettings):
    """
    Configuration for caching.

    Attributes:
        enabled: Whether caching is enabled.
        ttl: Time-to-live in seconds.
        directory: Cache directory path.
    """

    model_config = SettingsConfigDict(
        env_prefix="WAFFEN_CACHE_",
        extra="ignore",
    )

    enabled: bool = Field(default=True)
    ttl: int = Field(default=3600, ge=0)
    directory: Path = Field(default_factory=lambda: Path(".waffen_solver_cache"))


class WaffenSolverConfig(BaseSettings):
    """
    Main configuration class for Waffen-Solver.

    Aggregates all configuration sections and provides
    comprehensive settings management through environment
    variables and .env files.

    Attributes:
        llm: LLM provider configuration.
        git: Git integration configuration.
        codebase: Codebase scanning configuration.
        language: Language handling configuration.
        cache: Caching configuration.
        output_format: Output format preference.
        verbosity: Verbosity level.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WAFFEN_",
        extra="ignore",
    )

    llm: LLMConfig = Field(default_factory=LLMConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    codebase: CodebaseConfig = Field(default_factory=CodebaseConfig)
    language: LanguageConfig = Field(default_factory=LanguageConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    output_format: OutputFormat = Field(default=OutputFormat.RICH)
    verbosity: VerbosityLevel = Field(default=VerbosityLevel.NORMAL)

    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.verbosity == VerbosityLevel.DEBUG

    def is_verbose(self) -> bool:
        """Check if verbose or debug mode is enabled."""
        return self.verbosity in (VerbosityLevel.VERBOSE, VerbosityLevel.DEBUG)
