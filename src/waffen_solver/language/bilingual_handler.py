"""
Bilingual handling for Waffen-Solver.

Coordinates bilingual operations throughout the system
ensuring consistent language handling.
"""

import re
from typing import Optional

from waffen_solver.config.settings import Language, LLMConfig
from waffen_solver.language.detector import LanguageDetector
from waffen_solver.language.translator import TranslationService


class LanguagePreferences:
    """
    User language preferences.

    Attributes:
        default_language: Default output language.
        auto_detect: Whether to auto-detect input.
        prefer_bilingual: Whether to provide bilingual output.
    """

    def __init__(
        self,
        default_language: Language = Language.ENGLISH,
        auto_detect: bool = True,
        prefer_bilingual: bool = False,
    ) -> None:
        """Initialize language preferences."""
        self.default_language = default_language
        self.auto_detect = auto_detect
        self.prefer_bilingual = prefer_bilingual


class Content:
    """
    Content to be processed bilingually.

    Attributes:
        text: Content text.
        code_blocks: Extracted code blocks.
        has_code: Whether content has code.
    """

    def __init__(self, text: str) -> None:
        """Initialize content."""
        self.text = text
        self.code_blocks = self._extract_code_blocks(text)
        self.has_code = len(self.code_blocks) > 0

    def _extract_code_blocks(self, text: str) -> list:
        """Extract code blocks from text."""
        pattern = r"```[\s\S]*?```"
        return re.findall(pattern, text)


class BilingualOutput:
    """
    Bilingual output container.

    Attributes:
        english: English version.
        arabic: Arabic version.
        primary: Primary language version.
    """

    def __init__(
        self,
        english: str,
        arabic: str,
        primary_language: Language,
    ) -> None:
        """Initialize bilingual output."""
        self.english = english
        self.arabic = arabic
        self._primary_language = primary_language

    @property
    def primary(self) -> str:
        """Get primary language version."""
        if self._primary_language == Language.ARABIC:
            return self.arabic
        return self.english


class AnnotatedCode:
    """
    Code with language-aware annotations.

    Attributes:
        code: Original code.
        comments_language: Language of comments.
        translated_comments: Translated comments.
    """

    def __init__(
        self,
        code: str,
        comments_language: Language,
        translated_comments: Optional[str] = None,
    ) -> None:
        """Initialize annotated code."""
        self.code = code
        self.comments_language = comments_language
        self.translated_comments = translated_comments


class BilingualHandler:
    """
    Coordinates bilingual operations.

    Ensures consistent language handling throughout.

    Attributes:
        detector: Language detector.
        translator: Translation service.
        preferences: Language preferences.
    """

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        preferences: Optional[LanguagePreferences] = None,
    ) -> None:
        """
        Initialize bilingual handler.

        Args:
            llm_config: LLM configuration.
            preferences: Language preferences.
        """
        self._detector = LanguageDetector()
        self._translator = TranslationService(llm_config=llm_config)
        self._preferences = preferences or LanguagePreferences()

    @property
    def detector(self) -> LanguageDetector:
        """Get language detector."""
        return self._detector

    @property
    def translator(self) -> TranslationService:
        """Get translation service."""
        return self._translator

    @property
    def preferences(self) -> LanguagePreferences:
        """Get language preferences."""
        return self._preferences

    def determine_response_language(self, user_input: str) -> Language:
        """
        Determine appropriate response language.

        Args:
            user_input: User's input text.

        Returns:
            Language to use for response.
        """
        if not self._preferences.auto_detect:
            return self._preferences.default_language

        detection = self._detector.detect_language(user_input)

        if detection.confidence >= self._detector.confidence_threshold:
            return detection.language

        return self._preferences.default_language

    def format_bilingual_output(
        self,
        content: Content,
    ) -> BilingualOutput:
        """
        Format content for bilingual output.

        Args:
            content: Content to format.

        Returns:
            Bilingual output.
        """
        english_text = content.text
        arabic_text = content.text

        if not content.has_code:
            arabic_text = self._translator.translate(
                content.text,
                Language.ARABIC,
            )

        return BilingualOutput(
            english=english_text,
            arabic=arabic_text,
            primary_language=self._preferences.default_language,
        )

    def handle_code_comments(
        self,
        code: str,
        target_language: Language,
    ) -> AnnotatedCode:
        """
        Handle comments in code.

        Args:
            code: Code to process.
            target_language: Target language for comments.

        Returns:
            Annotated code.
        """
        current_lang = self._detect_comment_language(code)

        if current_lang == target_language:
            return AnnotatedCode(
                code=code,
                comments_language=current_lang,
            )

        translated = self._translate_comments(code, target_language)
        return AnnotatedCode(
            code=code,
            comments_language=current_lang,
            translated_comments=translated,
        )

    def translate_if_needed(
        self,
        text: str,
        target_language: Language,
    ) -> str:
        """
        Translate text if not in target language.

        Args:
            text: Text to possibly translate.
            target_language: Target language.

        Returns:
            Text in target language.
        """
        detection = self._detector.detect_language(text)

        if detection.language == target_language:
            return text

        return self._translator.translate(text, target_language)

    def _detect_comment_language(self, code: str) -> Language:
        """Detect language of comments in code."""
        comment_pattern = r"#.*$|\"\"\"[\s\S]*?\"\"\""
        comments = re.findall(comment_pattern, code, re.MULTILINE)

        if not comments:
            return Language.ENGLISH

        combined = " ".join(comments)
        detection = self._detector.detect_language(combined)
        return detection.language

    def _translate_comments(
        self,
        code: str,
        target_language: Language,
    ) -> str:
        """Translate comments in code."""
        def replace_comment(match: re.Match) -> str:
            comment = match.group(0)
            if comment.startswith("#"):
                content = comment[1:].strip()
                translated = self._translator.translate(content, target_language)
                return f"# {translated}"
            return comment

        pattern = r"#.*$"
        return re.sub(pattern, replace_comment, code, flags=re.MULTILINE)
