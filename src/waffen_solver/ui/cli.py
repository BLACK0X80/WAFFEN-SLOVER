"""
Command-line interface for Waffen-Solver.

Implements command pattern for CLI operations.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from waffen_solver.config.settings import WaffenSolverConfig, OutputFormat
from waffen_solver.core.engine import DebuggingEngine
from waffen_solver.core.explainer import ExplanationLevel
from waffen_solver.ui.formatter import OutputFormatter
from waffen_solver.ui.renderer import ResultRenderer


app = typer.Typer(
    name="waffen-solver",
    help="Enterprise-grade AI debugging assistant",
    add_completion=False,
)


class CLIConfig:
    """
    CLI configuration.

    Attributes:
        output_format: Output format.
        verbose: Verbose mode.
        language: Output language.
    """

    def __init__(
        self,
        output_format: OutputFormat = OutputFormat.RICH,
        verbose: bool = False,
    ) -> None:
        """Initialize CLI config."""
        self.output_format = output_format
        self.verbose = verbose


class CLI:
    """
    Command-line interface controller.

    Implements command pattern for CLI operations.

    Attributes:
        engine: Debugging engine.
        formatter: Output formatter.
        renderer: Result renderer.
        config: CLI configuration.
    """

    def __init__(
        self,
        config: Optional[WaffenSolverConfig] = None,
        cli_config: Optional[CLIConfig] = None,
    ) -> None:
        """
        Initialize CLI.

        Args:
            config: Application configuration.
            cli_config: CLI-specific configuration.
        """
        self._config = config or WaffenSolverConfig()
        self._cli_config = cli_config or CLIConfig()
        self._engine = DebuggingEngine(self._config)
        self._formatter = OutputFormatter(output_format=self._cli_config.output_format)
        self._renderer = ResultRenderer()
        self._console = Console()

    @property
    def engine(self) -> DebuggingEngine:
        """Get the debugging engine."""
        return self._engine

    @property
    def formatter(self) -> OutputFormatter:
        """Get the formatter."""
        return self._formatter

    @property
    def renderer(self) -> ResultRenderer:
        """Get the renderer."""
        return self._renderer

    def run(self) -> None:
        """Run the CLI application."""
        app()

    def analyze(self, error_input: str) -> None:
        """
        Analyze an error.

        Args:
            error_input: Error message to analyze.
        """
        result = self._engine.analyze_error(error_input)
        formatted = self._formatter.format_analysis(result)
        self._renderer.render_analysis(formatted)

        solutions = self._engine.generate_solutions(result)
        formatted_solutions = self._formatter.format_solutions(solutions)
        self._renderer.render_solutions(formatted_solutions)

    def explain(
        self,
        error_input: str,
        level: str = "simple",
    ) -> None:
        """
        Explain an error.

        Args:
            error_input: Error to explain.
            level: Explanation level.
        """
        result = self._engine.analyze_error(error_input)

        exp_level = ExplanationLevel(level)
        explanation = self._engine.explain_error(
            result.error,
            result.root_cause.description,
            exp_level,
        )

        formatted = self._formatter.format_explanation(explanation)
        self._renderer.render_explanation(formatted)

    def interactive(self) -> None:
        """Run interactive mode."""
        self._console.print(
            "[bold cyan]Waffen-Solver Interactive Mode[/]"
        )
        self._console.print("Enter 'quit' or 'exit' to leave.\n")

        while True:
            try:
                self._console.print("[bold]Paste your error:[/]")
                lines = []
                while True:
                    line = input()
                    if line.strip().lower() in ("", "---", "done"):
                        break
                    if line.strip().lower() in ("quit", "exit"):
                        return
                    lines.append(line)

                if not lines:
                    continue

                error_input = "\n".join(lines)
                self.analyze(error_input)

            except KeyboardInterrupt:
                self._console.print("\n[yellow]Interrupted.[/]")
                break
            except EOFError:
                break


@app.command()
def analyze(
    error: str = typer.Argument(..., help="Error message or stack trace to analyze"),
    context_path: Optional[Path] = typer.Option(
        None,
        "--context",
        "-c",
        help="Path to codebase for context",
    ),
    output_format: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich, plain, json",
    ),
) -> None:
    """Analyze an error and generate solutions."""
    config = WaffenSolverConfig()
    cli = CLI(config)

    if context_path and context_path.exists():
        cli.engine.learn_from_codebase(context_path)

    cli.analyze(error)


@app.command()
def explain(
    error: str = typer.Argument(..., help="Error message to explain"),
    level: str = typer.Option(
        "simple",
        "--level",
        "-l",
        help="Explanation level: simple, technical, deep_dive",
    ),
) -> None:
    """Get an explanation for an error."""
    config = WaffenSolverConfig()
    cli = CLI(config)
    cli.explain(error, level)


@app.command()
def scan(
    path: Path = typer.Argument(..., help="Path to codebase to scan"),
) -> None:
    """Scan and learn from a codebase."""
    config = WaffenSolverConfig()
    cli = CLI(config)
    console = Console()

    console.print(f"[cyan]Scanning codebase at {path}...[/]")
    context = cli.engine.learn_from_codebase(path)

    console.print(f"[green]Scan complete![/]")
    console.print(f"  Project type: {context.project_type.value}")
    console.print(f"  Dependencies: {len(context.dependencies)}")


@app.command(name="git-analyze")
def git_analyze(
    repo_path: Path = typer.Argument(..., help="Path to Git repository"),
) -> None:
    """Analyze Git history for debugging insights."""
    config = WaffenSolverConfig()
    cli = CLI(config)
    console = Console()

    console.print(f"[cyan]Analyzing Git history at {repo_path}...[/]")
    context = cli.engine.integrate_git_history(repo_path)

    console.print(f"[green]Analysis complete![/]")
    console.print(f"  Recent commits: {len(context.recent_commits)}")
    console.print(f"  Fragile areas: {len(context.fragile_areas)}")


@app.command()
def interactive() -> None:
    """Start interactive debugging session."""
    config = WaffenSolverConfig()
    cli = CLI(config)
    cli.interactive()


def main() -> None:
    """Main entry point."""
    app()
