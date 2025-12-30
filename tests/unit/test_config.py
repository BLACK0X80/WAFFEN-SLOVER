"""
Unit tests for configuration.
"""

import pytest

from waffen_solver.config.settings import (
    WaffenSolverConfig,
    LLMConfig,
    GitConfig,
    CodebaseConfig,
    LanguageConfig,
    CacheConfig,
    Language,
    OutputFormat,
    VerbosityLevel,
)
from waffen_solver.config.prompts import PromptTemplates


class TestConfiguration:
    """Tests for configuration classes."""

    def test_llm_config_defaults(self) -> None:
        """Test LLM config default values."""
        config = LLMConfig()
        assert config.provider == "anthropic"
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 4096
        assert 0 <= config.temperature <= 2

    def test_git_config_defaults(self) -> None:
        """Test Git config default values."""
        config = GitConfig()
        assert config.enabled is True
        assert config.history_limit == 100

    def test_codebase_config_defaults(self) -> None:
        """Test codebase config default values."""
        config = CodebaseConfig()
        assert config.enabled is True
        assert config.max_depth == 10
        assert "__pycache__" in config.excluded_patterns

    def test_language_config_defaults(self) -> None:
        """Test language config default values."""
        config = LanguageConfig()
        assert config.default == Language.ENGLISH
        assert config.translation_enabled is True

    def test_cache_config_defaults(self) -> None:
        """Test cache config default values."""
        config = CacheConfig()
        assert config.enabled is True
        assert config.ttl == 3600

    def test_main_config(self) -> None:
        """Test main configuration."""
        config = WaffenSolverConfig()
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.git, GitConfig)
        assert config.output_format == OutputFormat.RICH

    def test_debug_mode(self) -> None:
        """Test debug mode detection."""
        config = WaffenSolverConfig(verbosity=VerbosityLevel.DEBUG)
        assert config.is_debug() is True
        assert config.is_verbose() is True

    def test_normal_mode(self) -> None:
        """Test normal mode detection."""
        config = WaffenSolverConfig(verbosity=VerbosityLevel.NORMAL)
        assert config.is_debug() is False
        assert config.is_verbose() is False


class TestPromptTemplates:
    """Tests for prompt templates."""

    def test_templates_exist(self) -> None:
        """Test that all templates exist."""
        assert PromptTemplates.SYSTEM_PROMPT
        assert PromptTemplates.ERROR_ANALYSIS_TEMPLATE
        assert PromptTemplates.SOLUTION_GENERATION_TEMPLATE
        assert PromptTemplates.SIMPLE_EXPLANATION_TEMPLATE
        assert PromptTemplates.TRANSLATION_TEMPLATE

    def test_get_template(self) -> None:
        """Test getting template by name."""
        template = PromptTemplates.get_template("SYSTEM_PROMPT")
        assert "Waffen-Solver" in template

    def test_format_template(self) -> None:
        """Test template formatting."""
        result = PromptTemplates.format_template(
            "SIMPLE_EXPLANATION_TEMPLATE",
            error_message="Test error",
            root_cause="Test cause",
        )
        assert "Test error" in result
        assert "Test cause" in result
