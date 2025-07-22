import json
from pathlib import Path
from typing import Dict


class StatusManager:
    def __init__(self, path: Path):
        self.path = path
        self.status: Dict[str, str] = {}
        self._write()

    def update(self, key: str, value: str) -> None:
        self.status[key] = value
        self._write()

    def _write(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.status, f, indent=2)

    def load(self) -> Dict[str, str]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                self.status = json.load(f)
        return self.status
