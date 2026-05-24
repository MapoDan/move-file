from __future__ import annotations

import shutil
from pathlib import Path

from mutagen.id3 import ID3

from app.core.config import Settings


class CleanTagFileHandler:
    name = "clean-tag-file.py"

    def handle(self, file_path: Path, settings: Settings) -> None:
        audio = ID3(str(file_path))
        audio.delete(file_path)
        destination = Path(settings.dir_clean) / file_path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(destination))
