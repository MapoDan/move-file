from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.core.config import Settings


class FileHandler(Protocol):
    name: str

    def handle(self, file_path: Path, settings: Settings) -> None:
        ...
