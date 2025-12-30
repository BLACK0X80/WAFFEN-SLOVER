"""
Error explanation engine for Waffen-Solver.

Generates explanations at multiple abstraction levels
using Chain of Responsibility pattern.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from waffen_solver.config.settings import WaffenSolverConfig, Language
from waffen_solver.llm.provider import LLMProvider, GenerationConfig
from waffen_solver.llm.prompt_builder import PromptBuilder
from waffen_solver.llm.response_parser import ResponseParser
from waffen_solver.models.error import Error


class ExplanationLevel(str, Enum):
    """Levels of explanation detail."""

    SIMPLE = "simple"
    TECHNICAL = "technical"
    DEEP_DIVE = "deep_dive"


class Explanation:
    """
    Represents an error explanation.

    Attributes:
        content: Explanation text.
        level: Explanation level.
        language: Language of explanation.
        analogy: Optional analogy.
    """

    def __init__(
        self,
        content: str,
        level: ExplanationLevel,
        language: Language = Language.ENGLISH,
        analogy: Optional[str] = None,
    ) -> None:
        """Initialize explanation."""
        self.content = content
        self.level = level
        self.language = language
        self.analogy = analogy


class ExplanationHandler(ABC):
    """Abstract handler for explanation chain."""

    def __init__(self) -> None:
        """Initialize handler."""
        self._next_handler: Optional["ExplanationHandler"] = None

    def set_next(self, handler: "ExplanationHandler") -> "ExplanationHandler":
        """Set next handler in chain."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def can_handle(self, level: ExplanationLevel) -> bool:
        """Check if handler can process this level."""

    @abstractmethod
    def handle(
        self,
        error: Error,
        root_cause: str,
        llm_provider: LLMProvider,
        prompt_builder: PromptBuilder,
    ) -> str:
        """Handle explanation generation."""

    def process(
        self,
        level: ExplanationLevel,
        error: Error,
        root_cause: str,
        llm_provider: LLMProvider,
        prompt_builder: PromptBuilder,
    ) -> str:
        """Process through chain."""
        if self.can_handle(level):
            return self.handle(error, root_cause, llm_provider, prompt_builder)
        if self._next_handler:
            return self._next_handler.process(
                level, error, root_cause, llm_provider, prompt_builder
            )
        return ""


class SimpleExplanationHandler(ExplanationHandler):
    """Handler for simple explanations."""

    def can_handle(self, level: ExplanationLevel) -> bool:
        """Check if this handles simple level."""
        return level == ExplanationLevel.SIMPLE

    def handle(
        self,
        error: Error,
        root_cause: str,
        llm_provider: LLMProvider,
        prompt_builder: PromptBuilder,
    ) -> str:
        """Generate simple explanation."""
        prompt = prompt_builder.build_explanation_prompt(
            error, root_cause, "simple"
        )
        config = GenerationConfig(system_prompt=prompt_builder.get_system_prompt())
        return llm_provider.generate(prompt, config)


class TechnicalExplanationHandler(ExplanationHandler):
    """Handler for technical explanations."""

    def can_handle(self, level: ExplanationLevel) -> bool:
        """Check if this handles technical level."""
        return level == ExplanationLevel.TECHNICAL

    def handle(
        self,
        error: Error,
        root_cause: str,
        llm_provider: LLMProvider,
        prompt_builder: PromptBuilder,
    ) -> str:
        """Generate technical explanation."""
        prompt = prompt_builder.build_explanation_prompt(
            error, root_cause, "technical"
        )
        config = GenerationConfig(system_prompt=prompt_builder.get_system_prompt())
        return llm_provider.generate(prompt, config)


class DeepDiveExplanationHandler(ExplanationHandler):
    """Handler for deep dive explanations."""

    def can_handle(self, level: ExplanationLevel) -> bool:
        """Check if this handles deep dive level."""
        return level == ExplanationLevel.DEEP_DIVE

    def handle(
        self,
        error: Error,
        root_cause: str,
        llm_provider: LLMProvider,
        prompt_builder: PromptBuilder,
    ) -> str:
        """Generate deep dive explanation."""
        prompt = prompt_builder.build_explanation_prompt(
            error, root_cause, "deep_dive"
        )
        config = GenerationConfig(system_prompt=prompt_builder.get_system_prompt())
        return llm_provider.generate(prompt, config)


class ErrorExplainer:
    """
    Generates explanations at multiple abstraction levels.

    Uses Chain of Responsibility for different explanation levels.

    Attributes:
        llm_provider: LLM provider for generation.
        simplification_chain: Chain of explanation handlers.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        config: Optional[WaffenSolverConfig] = None,
    ) -> None:
        """
        Initialize error explainer.

        Args:
            llm_provider: LLM provider for generation.
            config: Optional configuration.
        """
        self._llm_provider = llm_provider
        self._config = config or WaffenSolverConfig()
        self._prompt_builder = PromptBuilder()
        self._response_parser = ResponseParser()
        self._chain = self._build_chain()

    def _build_chain(self) -> ExplanationHandler:
        """Build explanation handler chain."""
        simple_handler = SimpleExplanationHandler()
        technical_handler = TechnicalExplanationHandler()
        deep_dive_handler = DeepDiveExplanationHandler()

        simple_handler.set_next(technical_handler).set_next(deep_dive_handler)

        return simple_handler

    def explain(
        self,
        error: Error,
        root_cause: str,
        level: ExplanationLevel = ExplanationLevel.SIMPLE,
        language: Language = Language.ENGLISH,
    ) -> Explanation:
        """
        Generate explanation for an error.

        Args:
            error: Error to explain.
            root_cause: Root cause description.
            level: Explanation level.
            language: Target language.

        Returns:
            Generated explanation.
        """
        content = self._chain.process(
            level,
            error,
            root_cause,
            self._llm_provider,
            self._prompt_builder,
        )

        return Explanation(
            content=content,
            level=level,
            language=language,
        )

    def generate_simple_explanation(self, error: Error, root_cause: str) -> str:
        """Generate simple explanation."""
        return self.explain(error, root_cause, ExplanationLevel.SIMPLE).content

    def generate_technical_explanation(self, error: Error, root_cause: str) -> str:
        """Generate technical explanation."""
        return self.explain(error, root_cause, ExplanationLevel.TECHNICAL).content

    def generate_deep_dive_explanation(self, error: Error, root_cause: str) -> str:
        """Generate deep dive explanation."""
        return self.explain(error, root_cause, ExplanationLevel.DEEP_DIVE).content

    def create_analogy(self, error: Error, root_cause: str) -> str:
        """
        Create analogy for an error.

        Args:
            error: Error to explain.
            root_cause: Root cause description.

        Returns:
            Analogy text.
        """
        explanation = self.generate_simple_explanation(error, root_cause)
        return explanation
