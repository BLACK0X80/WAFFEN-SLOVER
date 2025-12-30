"""
Translation service for Waffen-Solver.

Handles translation between English and Arabic
while preserving technical terminology.
"""

from typing import Dict, List, Optional, Set

from waffen_solver.config.settings import Language, LLMConfig
from waffen_solver.llm.provider import LLMProvider, ClaudeProvider, GenerationConfig
from waffen_solver.llm.prompt_builder import PromptBuilder


class TechnicalTerminologyDict:
    """
    Dictionary of technical terms to preserve.

    Technical terms that should not be translated
    or should have specific translations.
    """

    PRESERVED_TERMS: Set[str] = {
        "API",
        "REST",
        "HTTP",
        "JSON",
        "XML",
        "SQL",
        "NoSQL",
        "Python",
        "JavaScript",
        "TypeScript",
        "Git",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "OAuth",
        "JWT",
        "CRUD",
        "CLI",
        "GUI",
        "IDE",
        "SDK",
        "URL",
        "URI",
        "DNS",
        "TCP",
        "UDP",
        "IP",
        "SSH",
        "SSL",
        "TLS",
        "HTML",
        "CSS",
        "DOM",
        "AJAX",
        "async",
        "await",
        "def",
        "class",
        "import",
        "return",
        "None",
        "True",
        "False",
    }

    def should_preserve(self, term: str) -> bool:
        """Check if term should be preserved."""
        return term in self.PRESERVED_TERMS or term.upper() in self.PRESERVED_TERMS

    def get_all_terms(self) -> Set[str]:
        """Get all preserved terms."""
        return self.PRESERVED_TERMS.copy()


class AnnotatedText:
    """
    Text with annotations for technical terms.

    Attributes:
        text: Original text.
        preserved_terms: Terms to preserve.
        term_positions: Positions of terms.
    """

    def __init__(
        self,
        text: str,
        preserved_terms: List[str],
    ) -> None:
        """Initialize annotated text."""
        self.text = text
        self.preserved_terms = preserved_terms


class TranslationCache:
    """Cache for translations."""

    def __init__(self) -> None:
        """Initialize translation cache."""
        self._cache: Dict[str, str] = {}

    def get(self, text: str, target: str) -> Optional[str]:
        """Get cached translation."""
        key = f"{target}:{hash(text)}"
        return self._cache.get(key)

    def set(self, text: str, target: str, translation: str) -> None:
        """Cache a translation."""
        key = f"{target}:{hash(text)}"
        self._cache[key] = translation


class TranslationService:
    """
    Handles translation between English and Arabic.

    Preserves technical terminology appropriately.

    Attributes:
        llm_provider: LLM provider for translation.
        terminology_dict: Technical terminology dictionary.
        cache: Translation cache.
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        llm_config: Optional[LLMConfig] = None,
    ) -> None:
        """
        Initialize translation service.

        Args:
            llm_provider: Optional LLM provider.
            llm_config: LLM configuration.
        """
        if llm_provider:
            self._llm_provider = llm_provider
        elif llm_config:
            self._llm_provider = ClaudeProvider(llm_config)
        else:
            self._llm_provider = None

        self._terminology_dict = TechnicalTerminologyDict()
        self._cache = TranslationCache()
        self._prompt_builder = PromptBuilder()

    @property
    def terminology_dict(self) -> TechnicalTerminologyDict:
        """Get terminology dictionary."""
        return self._terminology_dict

    @property
    def cache(self) -> TranslationCache:
        """Get translation cache."""
        return self._cache

    def translate(
        self,
        text: str,
        target_language: Language,
    ) -> str:
        """
        Translate text to target language.

        Args:
            text: Text to translate.
            target_language: Target language.

        Returns:
            Translated text.
        """
        if not text.strip():
            return text

        cached = self._cache.get(text, target_language.value)
        if cached:
            return cached

        if not self._llm_provider:
            return text

        annotated = self.preserve_technical_terms(text)

        target_name = "Arabic" if target_language == Language.ARABIC else "English"
        prompt = self._prompt_builder.build_translation_prompt(
            annotated.text,
            target_name,
        )

        config = GenerationConfig(
            system_prompt="You are a professional translator specializing in technical content."
        )

        translation = self._llm_provider.generate(prompt, config)
        self._cache.set(text, target_language.value, translation)

        return translation

    def preserve_technical_terms(self, text: str) -> AnnotatedText:
        """
        Annotate text with terms to preserve.

        Args:
            text: Text to annotate.

        Returns:
            Annotated text.
        """
        preserved: List[str] = []
        words = text.split()

        for word in words:
            clean_word = word.strip(".,;:!?()[]{}\"'")
            if self._terminology_dict.should_preserve(clean_word):
                if clean_word not in preserved:
                    preserved.append(clean_word)

        return AnnotatedText(text, preserved)

    def validate_translation(
        self,
        original: str,
        translated: str,
    ) -> bool:
        """
        Validate a translation.

        Args:
            original: Original text.
            translated: Translated text.

        Returns:
            True if translation appears valid.
        """
        if not translated.strip():
            return False

        if translated == original:
            return False

        preserved = self.preserve_technical_terms(original)
        for term in preserved.preserved_terms:
            if term not in translated:
                pass

        return True
