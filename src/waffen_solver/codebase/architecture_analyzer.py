"""
Architecture analysis for Waffen-Solver.

Analyzes overall system architecture and identifies
architectural patterns and styles.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

from waffen_solver.codebase.scanner import CodebaseScanner, ProjectStructure
from waffen_solver.codebase.parser import CodeParser
from waffen_solver.models.context import ArchitecturalStyle, ProjectType


class Layer:
    """
    Represents an architectural layer.

    Attributes:
        name: Layer name.
        directories: Directories in this layer.
        dependencies: Layers this depends on.
    """

    def __init__(
        self,
        name: str,
        directories: List[Path],
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Initialize layer."""
        self.name = name
        self.directories = directories
        self.dependencies = dependencies or []


class Component:
    """
    A component in the architecture.

    Attributes:
        name: Component name.
        path: Component path.
        type: Component type.
        dependencies: Component dependencies.
    """

    def __init__(
        self,
        name: str,
        path: Path,
        component_type: str,
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Initialize component."""
        self.name = name
        self.path = path
        self.type = component_type
        self.dependencies = dependencies or []


class ComponentMap:
    """
    Map of all components.

    Attributes:
        components: Dictionary of components.
    """

    def __init__(self) -> None:
        """Initialize component map."""
        self._components: Dict[str, Component] = {}

    def add(self, component: Component) -> None:
        """Add a component."""
        self._components[component.name] = component

    def get(self, name: str) -> Optional[Component]:
        """Get a component by name."""
        return self._components.get(name)

    def all(self) -> List[Component]:
        """Get all components."""
        return list(self._components.values())


class ModularityMetrics:
    """
    Modularity metrics for the codebase.

    Attributes:
        coupling: Coupling score.
        cohesion: Cohesion score.
        component_count: Number of components.
    """

    def __init__(
        self,
        coupling: float = 0.0,
        cohesion: float = 0.0,
        component_count: int = 0,
    ) -> None:
        """Initialize modularity metrics."""
        self.coupling = coupling
        self.cohesion = cohesion
        self.component_count = component_count


class DependencyAnalyzer:
    """Analyzes dependencies between components."""

    def __init__(self, parser: CodeParser) -> None:
        """Initialize with parser."""
        self._parser = parser

    def analyze_dependencies(
        self,
        files: List[Path],
    ) -> Dict[str, Set[str]]:
        """
        Analyze dependencies between files.

        Args:
            files: Files to analyze.

        Returns:
            Dependency map.
        """
        dependencies: Dict[str, Set[str]] = {}

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            tree = self._parser.parse_file(file_path)
            if not tree:
                continue

            imports = self._parser.identify_imports(tree)
            file_key = str(file_path)
            dependencies[file_key] = set()

            for imp in imports:
                dependencies[file_key].add(imp.module)

        return dependencies


class StructureAnalyzer:
    """Analyzes project structure."""

    LAYER_INDICATORS = {
        "controllers": "presentation",
        "views": "presentation",
        "routes": "presentation",
        "services": "business",
        "core": "business",
        "domain": "business",
        "models": "data",
        "repositories": "data",
        "database": "data",
        "utils": "infrastructure",
        "helpers": "infrastructure",
    }

    def identify_layers(self, structure: ProjectStructure) -> List[Layer]:
        """
        Identify architectural layers.

        Args:
            structure: Project structure.

        Returns:
            List of identified layers.
        """
        layer_dirs: Dict[str, List[Path]] = {}

        all_dirs = structure.source_dirs.copy()
        if structure.root:
            try:
                for item in structure.root.iterdir():
                    if item.is_dir():
                        all_dirs.append(item)
            except PermissionError:
                pass

        for directory in all_dirs:
            dir_name = directory.name.lower()
            for indicator, layer_name in self.LAYER_INDICATORS.items():
                if indicator in dir_name:
                    if layer_name not in layer_dirs:
                        layer_dirs[layer_name] = []
                    layer_dirs[layer_name].append(directory)

        layers: List[Layer] = []
        for name, dirs in layer_dirs.items():
            layers.append(Layer(name=name, directories=dirs))

        return layers


class ArchitecturalPatternRecognizer:
    """Recognizes architectural patterns."""

    def recognize(
        self,
        layers: List[Layer],
        component_count: int,
    ) -> ArchitecturalStyle:
        """
        Recognize architectural style.

        Args:
            layers: Identified layers.
            component_count: Number of components.

        Returns:
            Recognized architectural style.
        """
        layer_names = {layer.name for layer in layers}

        if {"presentation", "business", "data"} <= layer_names:
            return ArchitecturalStyle.LAYERED

        if component_count > 10:
            return ArchitecturalStyle.MONOLITH

        return ArchitecturalStyle.UNKNOWN


class ArchitectureAnalyzer:
    """
    Analyzes overall system architecture.

    Identifies architectural patterns and styles.

    Attributes:
        structure_analyzer: Structure analyzer.
        dependency_analyzer: Dependency analyzer.
        pattern_recognizer: Pattern recognizer.
    """

    def __init__(self) -> None:
        """Initialize architecture analyzer."""
        self._parser = CodeParser()
        self._structure_analyzer = StructureAnalyzer()
        self._dependency_analyzer = DependencyAnalyzer(self._parser)
        self._pattern_recognizer = ArchitecturalPatternRecognizer()

    @property
    def structure_analyzer(self) -> StructureAnalyzer:
        """Get structure analyzer."""
        return self._structure_analyzer

    @property
    def dependency_analyzer(self) -> DependencyAnalyzer:
        """Get dependency analyzer."""
        return self._dependency_analyzer

    @property
    def pattern_recognizer(self) -> ArchitecturalPatternRecognizer:
        """Get pattern recognizer."""
        return self._pattern_recognizer

    def analyze_architecture(
        self,
        root_path: Path,
    ) -> ArchitecturalStyle:
        """
        Analyze project architecture.

        Args:
            root_path: Project root path.

        Returns:
            Detected architectural style.
        """
        scanner = CodebaseScanner(root_path)
        structure = scanner.map_structure()

        layers = self.identify_layers(structure)
        components = self.map_components(structure)

        return self._pattern_recognizer.recognize(
            layers,
            len(components.all()),
        )

    def identify_layers(self, structure: ProjectStructure) -> List[Layer]:
        """
        Identify architectural layers.

        Args:
            structure: Project structure.

        Returns:
            List of layers.
        """
        return self._structure_analyzer.identify_layers(structure)

    def map_components(self, structure: ProjectStructure) -> ComponentMap:
        """
        Map all components.

        Args:
            structure: Project structure.

        Returns:
            Component map.
        """
        component_map = ComponentMap()

        for src_dir in structure.source_dirs:
            try:
                for item in src_dir.iterdir():
                    if item.is_dir():
                        component = Component(
                            name=item.name,
                            path=item,
                            component_type="module",
                        )
                        component_map.add(component)
            except PermissionError:
                pass

        return component_map

    def detect_architectural_style(
        self,
        root_path: Path,
    ) -> ArchitecturalStyle:
        """
        Detect the architectural style.

        Args:
            root_path: Project root.

        Returns:
            Architectural style.
        """
        return self.analyze_architecture(root_path)

    def assess_modularity(self, root_path: Path) -> ModularityMetrics:
        """
        Assess modularity of the codebase.

        Args:
            root_path: Project root.

        Returns:
            Modularity metrics.
        """
        scanner = CodebaseScanner(root_path)
        structure = scanner.map_structure()
        components = self.map_components(structure)

        return ModularityMetrics(
            coupling=0.5,
            cohesion=0.5,
            component_count=len(components.all()),
        )
