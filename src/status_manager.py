import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class StatusManager:
    def __init__(self, path: Path):
        self.path = path
        self.status: Dict[str, str] = {}
        self._write()
        logger.debug("Initialized StatusManager with %s", path)

    def update(self, key: str, value: str) -> None:
        self.status[key] = value
        self._write()
        logger.debug("Updated status %s=%s", key, value)

    def _write(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.status, f, indent=2)
        logger.debug("Wrote status to %s", self.path)

    def load(self) -> Dict[str, str]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                self.status = json.load(f)
            logger.debug("Loaded status from %s", self.path)
        return self.status
