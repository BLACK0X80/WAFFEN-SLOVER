"""
Code parsing for Waffen-Solver.

Parses code into Abstract Syntax Trees with
multi-language support.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Any


class ASTCache:
    """Cache for parsed ASTs."""

    def __init__(self) -> None:
        """Initialize AST cache."""
        self._cache: Dict[str, ast.AST] = {}

    def get(self, path: str) -> Optional[ast.AST]:
        """Get cached AST."""
        return self._cache.get(path)

    def set(self, path: str, tree: ast.AST) -> None:
        """Cache an AST."""
        self._cache[path] = tree


class FunctionInfo:
    """
    Information about a function.

    Attributes:
        name: Function name.
        line_start: Starting line.
        line_end: Ending line.
        args: Function arguments.
        returns: Return annotation.
        docstring: Function docstring.
    """

    def __init__(
        self,
        name: str,
        line_start: int,
        line_end: int,
        args: List[str],
        returns: Optional[str] = None,
        docstring: Optional[str] = None,
    ) -> None:
        """Initialize function info."""
        self.name = name
        self.line_start = line_start
        self.line_end = line_end
        self.args = args
        self.returns = returns
        self.docstring = docstring


class ClassInfo:
    """
    Information about a class.

    Attributes:
        name: Class name.
        line_start: Starting line.
        line_end: Ending line.
        bases: Base classes.
        methods: List of methods.
        docstring: Class docstring.
    """

    def __init__(
        self,
        name: str,
        line_start: int,
        line_end: int,
        bases: List[str],
        methods: List[FunctionInfo],
        docstring: Optional[str] = None,
    ) -> None:
        """Initialize class info."""
        self.name = name
        self.line_start = line_start
        self.line_end = line_end
        self.bases = bases
        self.methods = methods
        self.docstring = docstring


class ImportInfo:
    """
    Information about an import.

    Attributes:
        module: Imported module.
        names: Imported names.
        is_from: Whether it's a from import.
        line: Line number.
    """

    def __init__(
        self,
        module: str,
        names: List[str],
        is_from: bool = False,
        line: int = 0,
    ) -> None:
        """Initialize import info."""
        self.module = module
        self.names = names
        self.is_from = is_from
        self.line = line


class Definition:
    """
    A symbol definition.

    Attributes:
        name: Symbol name.
        kind: Definition kind.
        file_path: File containing definition.
        line: Line number.
    """

    def __init__(
        self,
        name: str,
        kind: str,
        file_path: Path,
        line: int,
    ) -> None:
        """Initialize definition."""
        self.name = name
        self.kind = kind
        self.file_path = file_path
        self.line = line


class CodeParser:
    """
    Parses code into Abstract Syntax Trees.

    Supports Python with extensibility for other languages.

    Attributes:
        ast_cache: Cache for parsed ASTs.
    """

    SUPPORTED_EXTENSIONS = {".py": "python"}

    def __init__(self) -> None:
        """Initialize code parser."""
        self._ast_cache = ASTCache()
        self._definitions: Dict[str, List[Definition]] = {}

    @property
    def ast_cache(self) -> ASTCache:
        """Get the AST cache."""
        return self._ast_cache

    def parse_file(self, file_path: Path) -> Optional[ast.AST]:
        """
        Parse a file into an AST.

        Args:
            file_path: Path to file.

        Returns:
            Parsed AST or None.
        """
        if file_path.suffix not in self.SUPPORTED_EXTENSIONS:
            return None

        cached = self._ast_cache.get(str(file_path))
        if cached:
            return cached

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            self._ast_cache.set(str(file_path), tree)
            return tree
        except (SyntaxError, OSError):
            return None

    def extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        """
        Extract functions from an AST.

        Args:
            tree: AST to extract from.

        Returns:
            List of function information.
        """
        functions: List[FunctionInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._extract_function_info(node)
                functions.append(func_info)

        return functions

    def extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        """
        Extract classes from an AST.

        Args:
            tree: AST to extract from.

        Returns:
            List of class information.
        """
        classes: List[ClassInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                classes.append(class_info)

        return classes

    def identify_imports(self, tree: ast.AST) -> List[ImportInfo]:
        """
        Identify imports in an AST.

        Args:
            tree: AST to analyze.

        Returns:
            List of import information.
        """
        imports: List[ImportInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        names=[alias.asname or alias.name],
                        is_from=False,
                        line=node.lineno,
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                imports.append(ImportInfo(
                    module=module,
                    names=names,
                    is_from=True,
                    line=node.lineno,
                ))

        return imports

    def find_definitions(self, symbol: str) -> List[Definition]:
        """
        Find definitions of a symbol.

        Args:
            symbol: Symbol to find.

        Returns:
            List of definitions.
        """
        return self._definitions.get(symbol, [])

    def index_file(self, file_path: Path) -> None:
        """
        Index definitions in a file.

        Args:
            file_path: File to index.
        """
        tree = self.parse_file(file_path)
        if not tree:
            return

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._add_definition(node.name, "function", file_path, node.lineno)
            elif isinstance(node, ast.ClassDef):
                self._add_definition(node.name, "class", file_path, node.lineno)

    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract information from function node."""
        args = [arg.arg for arg in node.args.args]
        returns = ast.unparse(node.returns) if node.returns else None
        docstring = ast.get_docstring(node)

        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            args=args,
            returns=returns,
            docstring=docstring,
        )

    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from class node."""
        bases = [ast.unparse(base) for base in node.bases]
        methods: List[FunctionInfo] = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function_info(item))

        docstring = ast.get_docstring(node)

        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            bases=bases,
            methods=methods,
            docstring=docstring,
        )

    def _add_definition(
        self,
        name: str,
        kind: str,
        file_path: Path,
        line: int,
    ) -> None:
        """Add a definition to the index."""
        definition = Definition(name, kind, file_path, line)
        if name not in self._definitions:
            self._definitions[name] = []
        self._definitions[name].append(definition)
