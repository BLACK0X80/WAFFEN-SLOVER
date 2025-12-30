"""
Main entry point for Waffen-Solver.

Provides the main application controller and
command-line interface.
"""

import sys
from typing import Optional

from waffen_solver.config.settings import WaffenSolverConfig
from waffen_solver.core.engine import DebuggingEngine
from waffen_solver.ui.cli import app, CLI
from waffen_solver.utils.logger import WaffenSolverLogger
from waffen_solver.exceptions import WaffenSolverException


class Application:
    """
    Main application controller.

    Coordinates initialization, execution, and cleanup.

    Attributes:
        config: Application configuration.
        engine: Debugging engine.
        cli: CLI controller.
        logger: Application logger.
    """

    def __init__(
        self,
        config: Optional[WaffenSolverConfig] = None,
    ) -> None:
        """
        Initialize application.

        Args:
            config: Optional configuration.
        """
        self._config = config or WaffenSolverConfig()
        self._logger = WaffenSolverLogger.get_instance(
            verbosity=self._config.verbosity,
        )
        self._engine: Optional[DebuggingEngine] = None
        self._cli: Optional[CLI] = None

    @property
    def config(self) -> WaffenSolverConfig:
        """Get configuration."""
        return self._config

    @property
    def engine(self) -> Optional[DebuggingEngine]:
        """Get debugging engine."""
        return self._engine

    @property
    def cli(self) -> Optional[CLI]:
        """Get CLI controller."""
        return self._cli

    @property
    def logger(self) -> WaffenSolverLogger:
        """Get logger."""
        return self._logger

    def initialize(self) -> None:
        """Initialize application components."""
        self._logger.info("Initializing Waffen-Solver...")
        self._engine = DebuggingEngine(self._config)
        self._cli = CLI(self._config)
        self._logger.info("Initialization complete")

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code.
        """
        try:
            self.initialize()
            app()
            return 0
        except WaffenSolverException as exc:
            return self.handle_error(exc)
        except KeyboardInterrupt:
            self._logger.info("Interrupted by user")
            return 130
        finally:
            self.cleanup()

    def handle_error(self, exception: WaffenSolverException) -> int:
        """
        Handle application error.

        Args:
            exception: Exception to handle.

        Returns:
            Exit code.
        """
        self._logger.log_exception(exception)

        from rich.console import Console
        console = Console(stderr=True)
        console.print(f"[red]Error:[/] {exception.get_user_message()}")

        if self._config.is_debug():
            console.print_exception()

        return 1

    def cleanup(self) -> None:
        """Clean up application resources."""
        self._logger.debug("Cleanup complete")


def main() -> None:
    """Main entry point function."""
    application = Application()
    exit_code = application.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
