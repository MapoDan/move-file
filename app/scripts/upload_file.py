from __future__ import annotations

from pathlib import Path

import requests
from mutagen.easyid3 import EasyID3

from app.core.config import Settings


class UploadFileHandler:
    name = "upload-file.py"

    def handle(self, file_path: Path, settings: Settings) -> None:
        tags = EasyID3(str(file_path))
        artist = tags.get("artist", ["Unknown Artist"])[0]
        album = tags.get("album", ["Unknown Album"])[0]
        title = tags.get("title", [file_path.stem])[0]
        track_raw = tags.get("tracknumber", ["0"])[0].split("/")[0]
        track = f"{int(track_raw):02d}" if track_raw.isdigit() else "00"

        new_name = f"{track} {title}.mp3"
        remote_path = f"{settings.nextcloud_root}/{artist}/{album}/{new_name}".replace("//", "/")
        url = f"{settings.nextcloud_url.rstrip('/')}/remote.php/dav/files/{settings.nextcloud_user}{remote_path}"

        with file_path.open("rb") as stream:
            response = requests.put(url, data=stream, auth=(settings.nextcloud_user, settings.nextcloud_password), timeout=120)
            response.raise_for_status()

        if settings.delete_after_upload:
            file_path.unlink(missing_ok=True)
