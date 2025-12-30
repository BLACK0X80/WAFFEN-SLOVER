"""
Language detection for Waffen-Solver.

Detects language from user input with support
for mixed-language content.
"""

import re
from typing import List, Optional

from waffen_solver.config.settings import Language


class DetectedLanguage:
    """
    Result of language detection.

    Attributes:
        language: Detected language.
        confidence: Detection confidence.
        is_mixed: Whether content is mixed language.
    """

    def __init__(
        self,
        language: Language,
        confidence: float,
        is_mixed: bool = False,
    ) -> None:
        """Initialize detected language."""
        self.language = language
        self.confidence = confidence
        self.is_mixed = is_mixed


class LanguageSegment:
    """
    A segment of text in a specific language.

    Attributes:
        text: Segment text.
        language: Segment language.
        start: Start position.
        end: End position.
    """

    def __init__(
        self,
        text: str,
        language: Language,
        start: int,
        end: int,
    ) -> None:
        """Initialize language segment."""
        self.text = text
        self.language = language
        self.start = start
        self.end = end


class LanguageClassifier:
    """
    Classifies text by language.

    Uses character-based heuristics for detection.
    """

    ARABIC_RANGE = (0x0600, 0x06FF)
    ARABIC_EXTENDED_RANGE = (0x0750, 0x077F)

    def is_arabic_char(self, char: str) -> bool:
        """Check if character is Arabic."""
        code = ord(char)
        return (
            self.ARABIC_RANGE[0] <= code <= self.ARABIC_RANGE[1] or
            self.ARABIC_EXTENDED_RANGE[0] <= code <= self.ARABIC_EXTENDED_RANGE[1]
        )

    def count_arabic_chars(self, text: str) -> int:
        """Count Arabic characters in text."""
        return sum(1 for char in text if self.is_arabic_char(char))

    def count_latin_chars(self, text: str) -> int:
        """Count Latin characters in text."""
        return sum(1 for char in text if char.isalpha() and ord(char) < 256)

    def classify(self, text: str) -> Language:
        """
        Classify text language.

        Args:
            text: Text to classify.

        Returns:
            Detected language.
        """
        arabic_count = self.count_arabic_chars(text)
        latin_count = self.count_latin_chars(text)

        if arabic_count > latin_count:
            return Language.ARABIC
        return Language.ENGLISH


class LanguageDetector:
    """
    Detects language from user input.

    Supports mixed-language detection.

    Attributes:
        classifier: Language classifier.
        confidence_threshold: Minimum confidence.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.6,
    ) -> None:
        """
        Initialize language detector.

        Args:
            confidence_threshold: Minimum confidence.
        """
        self._classifier = LanguageClassifier()
        self._confidence_threshold = confidence_threshold

    @property
    def classifier(self) -> LanguageClassifier:
        """Get the classifier."""
        return self._classifier

    @property
    def confidence_threshold(self) -> float:
        """Get confidence threshold."""
        return self._confidence_threshold

    def detect_language(self, text: str) -> DetectedLanguage:
        """
        Detect primary language of text.

        Args:
            text: Text to analyze.

        Returns:
            Detected language with confidence.
        """
        if not text.strip():
            return DetectedLanguage(Language.ENGLISH, 0.0)

        arabic_count = self._classifier.count_arabic_chars(text)
        latin_count = self._classifier.count_latin_chars(text)
        total = arabic_count + latin_count

        if total == 0:
            return DetectedLanguage(Language.ENGLISH, 0.0)

        arabic_ratio = arabic_count / total
        latin_ratio = latin_count / total

        is_mixed = 0.2 < arabic_ratio < 0.8

        if arabic_ratio > latin_ratio:
            return DetectedLanguage(
                Language.ARABIC,
                arabic_ratio,
                is_mixed,
            )
        return DetectedLanguage(
            Language.ENGLISH,
            latin_ratio,
            is_mixed,
        )

    def detect_mixed_language(self, text: str) -> List[LanguageSegment]:
        """
        Detect segments of different languages.

        Args:
            text: Text to analyze.

        Returns:
            List of language segments.
        """
        segments: List[LanguageSegment] = []

        words = text.split()
        current_lang: Optional[Language] = None
        current_start = 0
        current_words: List[str] = []

        for i, word in enumerate(words):
            word_lang = self._classifier.classify(word)

            if current_lang is None:
                current_lang = word_lang
                current_words = [word]
            elif word_lang == current_lang:
                current_words.append(word)
            else:
                segment_text = " ".join(current_words)
                segments.append(LanguageSegment(
                    text=segment_text,
                    language=current_lang,
                    start=current_start,
                    end=current_start + len(segment_text),
                ))
                current_lang = word_lang
                current_start = current_start + len(segment_text) + 1
                current_words = [word]

        if current_words and current_lang:
            segment_text = " ".join(current_words)
            segments.append(LanguageSegment(
                text=segment_text,
                language=current_lang,
                start=current_start,
                end=current_start + len(segment_text),
            ))

        return segments

    def get_confidence(self, text: str, language: Language) -> float:
        """
        Get confidence for specific language.

        Args:
            text: Text to analyze.
            language: Language to check.

        Returns:
            Confidence score.
        """
        detection = self.detect_language(text)
        if detection.language == language:
            return detection.confidence
        return 1.0 - detection.confidence
