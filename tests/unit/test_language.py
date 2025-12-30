"""
Unit tests for language detection and translation.
"""

import pytest

from waffen_solver.config.settings import Language
from waffen_solver.language.detector import LanguageDetector, LanguageClassifier
from waffen_solver.language.translator import (
    TranslationService,
    TechnicalTerminologyDict,
)
from waffen_solver.language.bilingual_handler import (
    BilingualHandler,
    LanguagePreferences,
    Content,
)


class TestLanguageClassifier:
    """Tests for language classifier."""

    def test_arabic_char_detection(self) -> None:
        """Test Arabic character detection."""
        classifier = LanguageClassifier()
        assert classifier.is_arabic_char("\u0627")
        assert not classifier.is_arabic_char("a")

    def test_count_arabic_chars(self) -> None:
        """Test counting Arabic characters."""
        classifier = LanguageClassifier()
        text = "Hello"
        assert classifier.count_arabic_chars(text) == 0

    def test_count_latin_chars(self) -> None:
        """Test counting Latin characters."""
        classifier = LanguageClassifier()
        text = "Hello World"
        assert classifier.count_latin_chars(text) == 10


class TestLanguageDetector:
    """Tests for language detector."""

    def test_detect_english(self) -> None:
        """Test English detection."""
        detector = LanguageDetector()
        result = detector.detect_language("Hello, this is a test message")
        assert result.language == Language.ENGLISH
        assert result.confidence > 0.5

    def test_detect_empty_text(self) -> None:
        """Test empty text detection."""
        detector = LanguageDetector()
        result = detector.detect_language("")
        assert result.confidence == 0.0

    def test_get_confidence(self) -> None:
        """Test confidence score."""
        detector = LanguageDetector()
        confidence = detector.get_confidence("Hello world", Language.ENGLISH)
        assert confidence > 0.5


class TestTechnicalTerminology:
    """Tests for technical terminology."""

    def test_preserved_terms(self) -> None:
        """Test term preservation."""
        dictionary = TechnicalTerminologyDict()
        assert dictionary.should_preserve("API")
        assert dictionary.should_preserve("Python")
        assert dictionary.should_preserve("JSON")
        assert not dictionary.should_preserve("hello")

    def test_get_all_terms(self) -> None:
        """Test getting all terms."""
        dictionary = TechnicalTerminologyDict()
        terms = dictionary.get_all_terms()
        assert "API" in terms
        assert len(terms) > 10


class TestTranslationService:
    """Tests for translation service."""

    def test_preserve_technical_terms(self) -> None:
        """Test technical term preservation."""
        service = TranslationService()
        result = service.preserve_technical_terms(
            "The API uses JSON and Python"
        )
        assert "API" in result.preserved_terms
        assert "JSON" in result.preserved_terms
        assert "Python" in result.preserved_terms


class TestBilingualHandler:
    """Tests for bilingual handler."""

    def test_language_preferences(self) -> None:
        """Test language preferences."""
        prefs = LanguagePreferences(
            default_language=Language.ARABIC,
            auto_detect=False,
        )
        assert prefs.default_language == Language.ARABIC
        assert prefs.auto_detect is False

    def test_content_parsing(self) -> None:
        """Test content parsing."""
        content = Content("Regular text without code")
        assert not content.has_code

        content_with_code = Content("Text with ```python\ncode\n```")
        assert content_with_code.has_code

    def test_determine_response_language_no_autodetect(self) -> None:
        """Test response language without auto-detect."""
        prefs = LanguagePreferences(
            default_language=Language.ARABIC,
            auto_detect=False,
        )
        handler = BilingualHandler(preferences=prefs)
        result = handler.determine_response_language("Hello world")
        assert result == Language.ARABIC
