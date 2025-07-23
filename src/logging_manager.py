import logging
from pathlib import Path


class LoggingManager:
    """Configure application-wide logging."""

    def __init__(self, path: Path, level: int = logging.INFO) -> None:
        self.path = path
        self.level = level
        self._configure()

    def _configure(self) -> None:
        """Set up logging handlers and format."""
        logging.basicConfig(
            level=self.level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(self.path),
                logging.StreamHandler(),
            ],
        )

