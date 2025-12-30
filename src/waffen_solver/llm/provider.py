"""
LLM provider implementations for Waffen-Solver.

Contains abstract base class and concrete implementations
for different LLM providers using adapter pattern.
"""

from abc import ABC, abstractmethod
from typing import Iterator, List, Optional

import anthropic

from waffen_solver.config.settings import LLMConfig
from waffen_solver.exceptions import LLMException, RateLimitException, TokenLimitException


class GenerationConfig:
    """
    Configuration for text generation.

    Attributes:
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.
        stop_sequences: Sequences to stop generation.
        system_prompt: System prompt to use.
    """

    def __init__(
        self,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        stop_sequences: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Initialize generation config."""
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.stop_sequences = stop_sequences or []
        self.system_prompt = system_prompt


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Implements adapter pattern for different LLM services.

    Attributes:
        config: LLM configuration.
    """

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize the LLM provider.

        Args:
            config: LLM configuration settings.
        """
        self._config = config

    @property
    def config(self) -> LLMConfig:
        """Get the provider configuration."""
        return self._config

    @abstractmethod
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt.
            config: Generation configuration.

        Returns:
            Generated text.
        """

    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> Iterator[str]:
        """
        Stream generate text from prompt.

        Args:
            prompt: Input prompt.
            config: Generation configuration.

        Yields:
            Generated text chunks.
        """

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Get token count for text.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens.
        """


class ClaudeProvider(LLMProvider):
    """
    Concrete implementation for Anthropic Claude.

    Optimized for Claude Sonnet 4 capabilities.

    Attributes:
        client: Anthropic API client.
    """

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize Claude provider.

        Args:
            config: LLM configuration.
        """
        super().__init__(config)
        api_key = config.api_key.get_secret_value()
        self._client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self._model = config.model

    @property
    def client(self) -> Optional[anthropic.Anthropic]:
        """Get the Anthropic client."""
        return self._client

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """
        Generate text using Claude.

        Args:
            prompt: Input prompt.
            config: Generation configuration.

        Returns:
            Generated text.

        Raises:
            LLMException: If generation fails.
        """
        if not self._client:
            raise LLMException("Anthropic client not initialized - API key missing")

        gen_config = config or self._default_config()

        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=gen_config.max_tokens,
                temperature=gen_config.temperature,
                system=gen_config.system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )
            return self._extract_text(message)
        except anthropic.RateLimitError as exc:
            raise RateLimitException("Claude API rate limit exceeded") from exc
        except anthropic.APIError as exc:
            raise LLMException(f"Claude API error: {exc}") from exc

    def stream_generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> Iterator[str]:
        """
        Stream generate text using Claude.

        Args:
            prompt: Input prompt.
            config: Generation configuration.

        Yields:
            Generated text chunks.
        """
        if not self._client:
            raise LLMException("Anthropic client not initialized - API key missing")

        gen_config = config or self._default_config()

        try:
            with self._client.messages.stream(
                model=self._model,
                max_tokens=gen_config.max_tokens,
                temperature=gen_config.temperature,
                system=gen_config.system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except anthropic.RateLimitError as exc:
            raise RateLimitException("Claude API rate limit exceeded") from exc
        except anthropic.APIError as exc:
            raise LLMException(f"Claude API error: {exc}") from exc

    def get_token_count(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses approximate calculation based on character count.

        Args:
            text: Text to count tokens for.

        Returns:
            Estimated number of tokens.
        """
        return len(text) // 4

    def _default_config(self) -> GenerationConfig:
        """Get default generation config."""
        return GenerationConfig(
            max_tokens=self._config.max_tokens,
            temperature=self._config.temperature,
        )

    def _extract_text(self, message: anthropic.types.Message) -> str:
        """Extract text from message response."""
        text_blocks = [
            block.text
            for block in message.content
            if hasattr(block, "text")
        ]
        return "".join(text_blocks)
