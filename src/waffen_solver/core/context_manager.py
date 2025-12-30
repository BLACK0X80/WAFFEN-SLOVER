"""
Context management for Waffen-Solver.

Manages and aggregates context from multiple sources
using Observer pattern for updates.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from waffen_solver.models.context import (
    AggregatedContext,
    CodebaseContext,
    SessionContext,
    EnvironmentContext,
    Context,
    ContextSource,
)
from waffen_solver.models.error import Error


class ContextObserver(ABC):
    """Abstract observer for context updates."""

    @abstractmethod
    def on_context_update(self, context: AggregatedContext) -> None:
        """Handle context update notification."""


class ContextUpdate:
    """
    Represents a context update.

    Attributes:
        source: Source of the update.
        data: Update data.
        timestamp: When update occurred.
    """

    def __init__(
        self,
        source: ContextSource,
        data: Dict[str, Any],
    ) -> None:
        """Initialize context update."""
        self.source = source
        self.data = data
        self.timestamp = datetime.now()


class RelevantContext:
    """
    Context relevant to a specific error.

    Attributes:
        error: The error this is relevant to.
        context_items: Relevant context items.
        relevance_scores: Scores for each item.
    """

    def __init__(
        self,
        error: Error,
        context_items: List[Context],
        relevance_scores: Dict[str, float],
    ) -> None:
        """Initialize relevant context."""
        self.error = error
        self.context_items = context_items
        self.relevance_scores = relevance_scores


class ContextManager:
    """
    Manages and aggregates context from multiple sources.

    Implements Observer pattern for context updates.

    Attributes:
        codebase_context: Codebase context.
        session_context: Session context.
        environment_context: Environment context.
    """

    def __init__(self) -> None:
        """Initialize context manager."""
        self._codebase_context: Optional[CodebaseContext] = None
        self._session_context: Optional[SessionContext] = None
        self._environment_context: Optional[EnvironmentContext] = None
        self._custom_contexts: List[Context] = []
        self._observers: List[ContextObserver] = []
        self._init_session()

    @property
    def codebase_context(self) -> Optional[CodebaseContext]:
        """Get codebase context."""
        return self._codebase_context

    @property
    def session_context(self) -> Optional[SessionContext]:
        """Get session context."""
        return self._session_context

    @property
    def environment_context(self) -> Optional[EnvironmentContext]:
        """Get environment context."""
        return self._environment_context

    def _init_session(self) -> None:
        """Initialize session context."""
        self._session_context = SessionContext(
            session_id=str(uuid4()),
            start_time=datetime.now(),
        )

    def register_observer(self, observer: ContextObserver) -> None:
        """
        Register an observer for context updates.

        Args:
            observer: Observer to register.
        """
        self._observers.append(observer)

    def unregister_observer(self, observer: ContextObserver) -> None:
        """
        Unregister an observer.

        Args:
            observer: Observer to remove.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def set_codebase_context(self, context: CodebaseContext) -> None:
        """
        Set codebase context.

        Args:
            context: Codebase context to set.
        """
        self._codebase_context = context
        self._notify_observers()

    def set_environment_context(self, context: EnvironmentContext) -> None:
        """
        Set environment context.

        Args:
            context: Environment context to set.
        """
        self._environment_context = context
        self._notify_observers()

    def update_context(self, update: ContextUpdate) -> None:
        """
        Apply a context update.

        Args:
            update: Context update to apply.
        """
        if update.source == ContextSource.CODEBASE and self._codebase_context:
            self._apply_codebase_update(update)
        elif update.source == ContextSource.SESSION and self._session_context:
            self._apply_session_update(update)
        elif update.source == ContextSource.ENVIRONMENT and self._environment_context:
            self._apply_environment_update(update)
        else:
            self._add_custom_context(update)

        self._notify_observers()

    def build_context(self) -> AggregatedContext:
        """
        Build aggregated context from all sources.

        Returns:
            Aggregated context.
        """
        return AggregatedContext(
            codebase=self._codebase_context,
            session=self._session_context,
            environment=self._environment_context,
            custom_contexts=self._custom_contexts.copy(),
        )

    def get_relevant_context(self, error: Error) -> RelevantContext:
        """
        Get context relevant to a specific error.

        Args:
            error: Error to find context for.

        Returns:
            Relevant context.
        """
        context_items: List[Context] = []
        relevance_scores: Dict[str, float] = {}

        if self._codebase_context:
            context_items.append(Context(
                source=ContextSource.CODEBASE,
                data={"context": self._codebase_context.model_dump()},
            ))
            relevance_scores["codebase"] = self._score_codebase_relevance(error)

        if self._session_context:
            context_items.append(Context(
                source=ContextSource.SESSION,
                data={"context": self._session_context.model_dump()},
            ))
            relevance_scores["session"] = 0.5

        return RelevantContext(
            error=error,
            context_items=context_items,
            relevance_scores=relevance_scores,
        )

    def add_error_to_session(self, error: Error) -> None:
        """
        Add error to session history.

        Args:
            error: Error to add.
        """
        if self._session_context:
            self._session_context.previous_errors.append(error.raw_message)

    def _apply_codebase_update(self, update: ContextUpdate) -> None:
        """Apply update to codebase context."""
        if self._codebase_context:
            for key, value in update.data.items():
                if hasattr(self._codebase_context, key):
                    setattr(self._codebase_context, key, value)

    def _apply_session_update(self, update: ContextUpdate) -> None:
        """Apply update to session context."""
        if self._session_context:
            for key, value in update.data.items():
                if hasattr(self._session_context, key):
                    setattr(self._session_context, key, value)

    def _apply_environment_update(self, update: ContextUpdate) -> None:
        """Apply update to environment context."""
        if self._environment_context:
            for key, value in update.data.items():
                if hasattr(self._environment_context, key):
                    setattr(self._environment_context, key, value)

    def _add_custom_context(self, update: ContextUpdate) -> None:
        """Add custom context from update."""
        context = Context(
            source=update.source,
            timestamp=update.timestamp,
            data=update.data,
        )
        self._custom_contexts.append(context)

    def _notify_observers(self) -> None:
        """Notify all observers of context update."""
        aggregated = self.build_context()
        for observer in self._observers:
            observer.on_context_update(aggregated)

    def _score_codebase_relevance(self, error: Error) -> float:
        """Score relevance of codebase context to error."""
        if not self._codebase_context:
            return 0.0

        if error.source_file:
            return 0.8
        return 0.5
