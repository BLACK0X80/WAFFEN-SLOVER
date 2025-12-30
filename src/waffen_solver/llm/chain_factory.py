"""
LangChain chain factory for Waffen-Solver.

Creates LangChain chains for different operations
using factory pattern.
"""

from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from waffen_solver.config.settings import LLMConfig
from waffen_solver.config.prompts import PromptTemplates


class ChainFactory:
    """
    Creates LangChain chains for different operations.

    Implements factory pattern for chain creation.

    Attributes:
        llm: LangChain LLM instance.
    """

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize chain factory.

        Args:
            config: LLM configuration.
        """
        self._config = config
        api_key = config.api_key.get_secret_value()
        self._llm: Optional[ChatAnthropic] = None
        if api_key:
            self._llm = ChatAnthropic(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                api_key=api_key,
            )

    @property
    def llm(self) -> Optional[ChatAnthropic]:
        """Get the LangChain LLM instance."""
        return self._llm

    def create_analysis_chain(self) -> Runnable:
        """
        Create chain for error analysis.

        Returns:
            Analysis chain runnable.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptTemplates.SYSTEM_PROMPT),
            ("human", PromptTemplates.ERROR_ANALYSIS_TEMPLATE),
        ])

        return prompt | self._llm | StrOutputParser()

    def create_solution_chain(self) -> Runnable:
        """
        Create chain for solution generation.

        Returns:
            Solution chain runnable.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptTemplates.SYSTEM_PROMPT),
            ("human", PromptTemplates.SOLUTION_GENERATION_TEMPLATE),
        ])

        return prompt | self._llm | StrOutputParser()

    def create_explanation_chain(self, level: str = "simple") -> Runnable:
        """
        Create chain for error explanation.

        Args:
            level: Explanation level.

        Returns:
            Explanation chain runnable.
        """
        template_map = {
            "simple": PromptTemplates.SIMPLE_EXPLANATION_TEMPLATE,
            "technical": PromptTemplates.TECHNICAL_EXPLANATION_TEMPLATE,
            "deep_dive": PromptTemplates.DEEP_DIVE_EXPLANATION_TEMPLATE,
        }

        template = template_map.get(level, PromptTemplates.SIMPLE_EXPLANATION_TEMPLATE)

        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptTemplates.SYSTEM_PROMPT),
            ("human", template),
        ])

        return prompt | self._llm | StrOutputParser()

    def create_translation_chain(self) -> Runnable:
        """
        Create chain for translation.

        Returns:
            Translation chain runnable.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional translator specializing in technical content."),
            ("human", PromptTemplates.TRANSLATION_TEMPLATE),
        ])

        return prompt | self._llm | StrOutputParser()

    def create_codebase_learning_chain(self) -> Runnable:
        """
        Create chain for codebase learning.

        Returns:
            Codebase learning chain runnable.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptTemplates.SYSTEM_PROMPT),
            ("human", PromptTemplates.CODEBASE_LEARNING_TEMPLATE),
        ])

        return prompt | self._llm | StrOutputParser()

    def create_git_analysis_chain(self) -> Runnable:
        """
        Create chain for Git analysis.

        Returns:
            Git analysis chain runnable.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptTemplates.SYSTEM_PROMPT),
            ("human", PromptTemplates.GIT_ANALYSIS_TEMPLATE),
        ])

        return prompt | self._llm | StrOutputParser()
