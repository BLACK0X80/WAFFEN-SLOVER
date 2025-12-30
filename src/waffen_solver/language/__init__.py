"""Language support module for Waffen-Solver."""

from waffen_solver.language.translator import TranslationService
from waffen_solver.language.detector import LanguageDetector
from waffen_solver.language.bilingual_handler import BilingualHandler

__all__ = [
    "TranslationService",
    "LanguageDetector",
    "BilingualHandler",
]
