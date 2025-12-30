"""
Pattern detection for Waffen-Solver.

Detects design patterns and code smells using
heuristics and pattern matching.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional

from waffen_solver.codebase.parser import CodeParser, ClassInfo
from waffen_solver.models.context import DetectedPattern


class Heuristic:
    """
    Base class for pattern heuristics.

    Attributes:
        name: Heuristic name.
        description: Heuristic description.
    """

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize heuristic."""
        self.name = name
        self.description = description

    def check(self, class_info: ClassInfo) -> bool:
        """
        Check if heuristic matches.

        Args:
            class_info: Class to check.

        Returns:
            True if matches.
        """
        return False


class SingletonHeuristic(Heuristic):
    """Heuristic for detecting singleton pattern."""

    def __init__(self) -> None:
        """Initialize singleton heuristic."""
        super().__init__("Singleton", "Detects singleton pattern")

    def check(self, class_info: ClassInfo) -> bool:
        """Check for singleton indicators."""
        for method in class_info.methods:
            if method.name in ("get_instance", "instance", "_instance"):
                return True
        return False


class FactoryHeuristic(Heuristic):
    """Heuristic for detecting factory pattern."""

    def __init__(self) -> None:
        """Initialize factory heuristic."""
        super().__init__("Factory", "Detects factory pattern")

    def check(self, class_info: ClassInfo) -> bool:
        """Check for factory indicators."""
        if "Factory" in class_info.name:
            return True
        for method in class_info.methods:
            if method.name.startswith("create"):
                return True
        return False


class ObserverHeuristic(Heuristic):
    """Heuristic for detecting observer pattern."""

    def __init__(self) -> None:
        """Initialize observer heuristic."""
        super().__init__("Observer", "Detects observer pattern")

    def check(self, class_info: ClassInfo) -> bool:
        """Check for observer indicators."""
        observer_methods = {"subscribe", "unsubscribe", "notify", "attach", "detach"}
        method_names = {m.name for m in class_info.methods}
        return len(observer_methods & method_names) >= 2


class AntiPattern:
    """
    Represents an anti-pattern or code smell.

    Attributes:
        name: Anti-pattern name.
        description: Description.
        severity: Severity level.
        location: Location in code.
    """

    def __init__(
        self,
        name: str,
        description: str,
        severity: str = "medium",
        location: str = "",
    ) -> None:
        """Initialize anti-pattern."""
        self.name = name
        self.description = description
        self.severity = severity
        self.location = location


class CodingConventions:
    """
    Detected coding conventions.

    Attributes:
        naming_style: Variable naming style.
        docstring_style: Docstring format.
        import_style: Import organization.
    """

    def __init__(self) -> None:
        """Initialize coding conventions."""
        self.naming_style: str = ""
        self.docstring_style: str = ""
        self.import_style: str = ""


class Abstraction:
    """
    A custom abstraction in the codebase.

    Attributes:
        name: Abstraction name.
        kind: Kind of abstraction.
        files: Files implementing this.
    """

    def __init__(
        self,
        name: str,
        kind: str,
        files: List[str],
    ) -> None:
        """Initialize abstraction."""
        self.name = name
        self.kind = kind
        self.files = files


class PatternLibrary:
    """Library of known patterns."""

    PATTERNS = {
        "Singleton": "Single instance pattern",
        "Factory": "Object creation pattern",
        "Observer": "Event subscription pattern",
        "Strategy": "Interchangeable algorithms pattern",
        "Decorator": "Dynamic behavior extension pattern",
        "Adapter": "Interface compatibility pattern",
        "Template Method": "Skeletal algorithm pattern",
    }

    def get_description(self, name: str) -> str:
        """Get pattern description."""
        return self.PATTERNS.get(name, "")


class PatternDetector:
    """
    Detects design patterns and code smells.

    Uses heuristics for pattern detection.

    Attributes:
        pattern_library: Pattern library.
        heuristics: List of heuristics.
    """

    def __init__(self) -> None:
        """Initialize pattern detector."""
        self._pattern_library = PatternLibrary()
        self._heuristics: List[Heuristic] = [
            SingletonHeuristic(),
            FactoryHeuristic(),
            ObserverHeuristic(),
        ]
        self._parser = CodeParser()

    @property
    def pattern_library(self) -> PatternLibrary:
        """Get the pattern library."""
        return self._pattern_library

    @property
    def heuristics(self) -> List[Heuristic]:
        """Get the heuristics."""
        return self._heuristics

    def detect_patterns(self, files: List[Path]) -> List[DetectedPattern]:
        """
        Detect patterns in a list of files.

        Args:
            files: Files to analyze.

        Returns:
            List of detected patterns.
        """
        pattern_locations: Dict[str, List[str]] = {}

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            tree = self._parser.parse_file(file_path)
            if not tree:
                continue

            classes = self._parser.extract_classes(tree)
            for class_info in classes:
                for heuristic in self._heuristics:
                    if heuristic.check(class_info):
                        if heuristic.name not in pattern_locations:
                            pattern_locations[heuristic.name] = []
                        pattern_locations[heuristic.name].append(
                            f"{file_path}:{class_info.name}"
                        )

        patterns: List[DetectedPattern] = []
        for name, locations in pattern_locations.items():
            confidence = min(0.3 + len(locations) * 0.1, 0.9)
            patterns.append(DetectedPattern(
                name=name,
                locations=locations,
                confidence=confidence,
            ))

        return patterns

    def identify_anti_patterns(self, files: List[Path]) -> List[AntiPattern]:
        """
        Identify anti-patterns in code.

        Args:
            files: Files to analyze.

        Returns:
            List of anti-patterns.
        """
        anti_patterns: List[AntiPattern] = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            tree = self._parser.parse_file(file_path)
            if not tree:
                continue

            classes = self._parser.extract_classes(tree)
            for class_info in classes:
                if len(class_info.methods) > 20:
                    anti_patterns.append(AntiPattern(
                        name="God Class",
                        description=f"Class {class_info.name} has too many methods",
                        severity="medium",
                        location=str(file_path),
                    ))

                if len(class_info.bases) > 3:
                    anti_patterns.append(AntiPattern(
                        name="Excessive Inheritance",
                        description=f"Class {class_info.name} inherits from too many classes",
                        severity="low",
                        location=str(file_path),
                    ))

        return anti_patterns

    def recognize_conventions(self, files: List[Path]) -> CodingConventions:
        """
        Recognize coding conventions.

        Args:
            files: Files to analyze.

        Returns:
            Detected conventions.
        """
        conventions = CodingConventions()

        snake_case_count = 0
        camel_case_count = 0

        for file_path in files[:20]:
            if file_path.suffix != ".py":
                continue

            tree = self._parser.parse_file(file_path)
            if not tree:
                continue

            functions = self._parser.extract_functions(tree)
            for func in functions:
                if "_" in func.name:
                    snake_case_count += 1
                elif func.name[0].islower() and any(c.isupper() for c in func.name):
                    camel_case_count += 1

        if snake_case_count > camel_case_count:
            conventions.naming_style = "snake_case"
        elif camel_case_count > snake_case_count:
            conventions.naming_style = "camelCase"

        conventions.docstring_style = "google"

        return conventions

    def find_custom_abstractions(self, files: List[Path]) -> List[Abstraction]:
        """
        Find custom abstractions in codebase.

        Args:
            files: Files to analyze.

        Returns:
            List of abstractions.
        """
        abstractions: List[Abstraction] = []
        base_classes: Dict[str, List[str]] = {}

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            tree = self._parser.parse_file(file_path)
            if not tree:
                continue

            classes = self._parser.extract_classes(tree)
            for class_info in classes:
                for base in class_info.bases:
                    if base not in base_classes:
                        base_classes[base] = []
                    base_classes[base].append(str(file_path))

        for base, files_list in base_classes.items():
            if len(files_list) >= 2:
                abstractions.append(Abstraction(
                    name=base,
                    kind="base_class",
                    files=files_list,
                ))

        return abstractions
