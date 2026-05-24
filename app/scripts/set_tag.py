from __future__ import annotations

from pathlib import Path

import requests

from app.core.config import Settings


class SetTagHandler:
    name = "set-tag.py"

    def handle(self, file_path: Path, settings: Settings) -> None:
        payload = {"file": str(file_path)}
        response = requests.post(
            settings.onetagger_url,
            json=payload,
            timeout=settings.onetagger_timeout_seconds,
        )
        response.raise_for_status()
