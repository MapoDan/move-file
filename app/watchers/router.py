from __future__ import annotations

from pathlib import Path

from app.core.config import Settings
from app.scripts.clean_tag_file import CleanTagFileHandler
from app.scripts.set_tag import SetTagHandler
from app.scripts.upload_file import UploadFileHandler


class HandlerRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mapping = {
            Path(settings.input_dir).resolve(): CleanTagFileHandler(),
            Path(settings.dir_clean).resolve(): SetTagHandler(),
            Path(settings.dir_tagged).resolve(): UploadFileHandler(),
        }

    def resolve(self, file_path: Path):
        rp = file_path.resolve()
        for root, handler in self.mapping.items():
            if root in [rp, *rp.parents]:
                return root, handler
        return None, None
