"""
Result rendering for Waffen-Solver.

Renders formatted results to terminal using Rich
with progressive disclosure and interactivity.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.style import Style
from rich.markdown import Markdown

from waffen_solver.ui.formatter import FormattedOutput


class Theme:
    """
    Theme configuration for rendering.

    Attributes:
        primary_color: Primary color.
        secondary_color: Secondary color.
        success_color: Success color.
        warning_color: Warning color.
        error_color: Error color.
    """

    def __init__(
        self,
        primary_color: str = "cyan",
        secondary_color: str = "blue",
        success_color: str = "green",
        warning_color: str = "yellow",
        error_color: str = "red",
    ) -> None:
        """Initialize theme."""
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.success_color = success_color
        self.warning_color = warning_color
        self.error_color = error_color


class TableData:
    """
    Data for table rendering.

    Attributes:
        title: Table title.
        columns: Column names.
        rows: Table rows.
    """

    def __init__(
        self,
        title: str,
        columns: List[str],
        rows: List[List[str]],
    ) -> None:
        """Initialize table data."""
        self.title = title
        self.columns = columns
        self.rows = rows


class TreeStructure:
    """
    Data for tree rendering.

    Attributes:
        label: Root label.
        children: Child nodes.
    """

    def __init__(
        self,
        label: str,
        children: Optional[List["TreeStructure"]] = None,
    ) -> None:
        """Initialize tree structure."""
        self.label = label
        self.children = children or []


class ResultRenderer:
    """
    Renders formatted results to terminal using Rich.

    Handles progressive disclosure and interactivity.

    Attributes:
        console: Rich console.
        theme: Rendering theme.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        theme: Optional[Theme] = None,
    ) -> None:
        """
        Initialize result renderer.

        Args:
            console: Rich console.
            theme: Rendering theme.
        """
        self._console = console or Console()
        self._theme = theme or Theme()

    @property
    def console(self) -> Console:
        """Get the console."""
        return self._console

    @property
    def theme(self) -> Theme:
        """Get the theme."""
        return self._theme

    def render(self, output: FormattedOutput) -> None:
        """
        Render formatted output.

        Args:
            output: Formatted output to render.
        """
        for section in output.sections:
            self._render_section(section)
        self._console.print()

    def render_analysis(self, output: FormattedOutput) -> None:
        """
        Render analysis output.

        Args:
            output: Analysis output.
        """
        self.render(output)

    def render_solutions(self, output: FormattedOutput) -> None:
        """
        Render solutions output.

        Args:
            output: Solutions output.
        """
        self.render(output)

    def render_explanation(self, output: FormattedOutput) -> None:
        """
        Render explanation output.

        Args:
            output: Explanation output.
        """
        self.render(output)

    def create_table(self, data: TableData) -> Table:
        """
        Create a Rich table.

        Args:
            data: Table data.

        Returns:
            Rich Table.
        """
        table = Table(title=data.title)

        for column in data.columns:
            table.add_column(column)

        for row in data.rows:
            table.add_row(*row)

        return table

    def create_tree(self, structure: TreeStructure) -> Tree:
        """
        Create a Rich tree.

        Args:
            structure: Tree structure.

        Returns:
            Rich Tree.
        """
        tree = Tree(structure.label)
        self._add_tree_children(tree, structure.children)
        return tree

    def _render_section(self, section: Dict[str, Any]) -> None:
        """Render a single section."""
        section_type = section.get("type", "")

        if section_type == "header":
            self._render_header(section)
        elif section_type == "panel":
            self._render_panel(section)
        elif section_type == "info":
            self._render_info(section)
        elif section_type == "list":
            self._render_list(section)
        elif section_type == "solution":
            self._render_solution(section)
        elif section_type == "text":
            self._render_text(section)

    def _render_header(self, section: Dict[str, Any]) -> None:
        """Render header section."""
        title = section.get("title", "")
        subtitle = section.get("subtitle", "")

        self._console.print()
        self._console.rule(f"[bold {self._theme.primary_color}]{title}")
        if subtitle:
            self._console.print(
                f"  [{self._theme.secondary_color}]{subtitle}[/]",
                justify="center",
            )

    def _render_panel(self, section: Dict[str, Any]) -> None:
        """Render panel section."""
        title = section.get("title", "")
        content = section.get("content", "")
        style = section.get("style", self._theme.primary_color)

        panel = Panel(
            content,
            title=title,
            border_style=style,
        )
        self._console.print(panel)

    def _render_info(self, section: Dict[str, Any]) -> None:
        """Render info section."""
        items = section.get("items", [])

        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold")
        table.add_column("Value")

        for key, value in items:
            table.add_row(key, str(value))

        self._console.print(table)

    def _render_list(self, section: Dict[str, Any]) -> None:
        """Render list section."""
        title = section.get("title", "")
        items = section.get("items", [])

        if title:
            self._console.print(f"\n[bold]{title}:[/]")

        for item in items:
            self._console.print(f"  [dim]-[/] {item}")

    def _render_solution(self, section: Dict[str, Any]) -> None:
        """Render solution section."""
        rank = section.get("rank", 0)
        score = section.get("score", 0.0)
        title = section.get("title", "")
        approach = section.get("approach", "")
        complexity = section.get("complexity", "")
        risk = section.get("risk", "")
        pros = section.get("pros", [])
        cons = section.get("cons", [])

        header = f"[bold]#{rank}[/] {title} [dim](Score: {score:.0%})[/]"

        content_lines = [
            f"[bold]Approach:[/] {approach}",
            f"[bold]Complexity:[/] {complexity} | [bold]Risk:[/] {risk}",
        ]

        if pros:
            content_lines.append(f"\n[{self._theme.success_color}]Pros:[/]")
            for pro in pros:
                content_lines.append(f"  + {pro}")

        if cons:
            content_lines.append(f"\n[{self._theme.warning_color}]Cons:[/]")
            for con in cons:
                content_lines.append(f"  - {con}")

        panel = Panel(
            "\n".join(content_lines),
            title=header,
            border_style=self._theme.secondary_color,
        )
        self._console.print(panel)

    def _render_text(self, section: Dict[str, Any]) -> None:
        """Render text section."""
        content = section.get("content", "")
        self._console.print(Markdown(content))

    def _add_tree_children(
        self,
        tree: Tree,
        children: List[TreeStructure],
    ) -> None:
        """Add children to tree recursively."""
        for child in children:
            subtree = tree.add(child.label)
            self._add_tree_children(subtree, child.children)
