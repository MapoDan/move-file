from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    input_dir: str = os.getenv("INPUT_DIR", "/data/input")
    dir_clean: str = os.getenv("DIR_CLEAN", "/data/clean")
    dir_tagged: str = os.getenv("DIR_TAGGED", "/data/tagged")

    recursive_watch: bool = _bool_env("RECURSIVE_WATCH", True)
    stability_seconds: int = _int_env("FILE_STABILITY_SECONDS", 15)
    stability_poll_seconds: int = _int_env("FILE_STABILITY_POLL_SECONDS", 2)

    max_retries: int = _int_env("MAX_RETRIES", 3)
    retry_delay_seconds: int = _int_env("RETRY_DELAY_SECONDS", 5)

    processed_db_path: str = os.getenv("PROCESSED_DB_PATH", "/data/state/processed.sqlite3")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    onetagger_url: str = os.getenv("ONETAGGER_URL", "http://onetagger:8080/tag")
    onetagger_timeout_seconds: int = _int_env("ONETAGGER_TIMEOUT_SECONDS", 60)

    nextcloud_url: str = os.getenv("NEXTCLOUD_URL", "")
    nextcloud_user: str = os.getenv("NEXTCLOUD_USER", "")
    nextcloud_password: str = os.getenv("NEXTCLOUD_PASSWORD", "")
    nextcloud_root: str = os.getenv("NEXTCLOUD_ROOT", "/Music")
    delete_after_upload: bool = _bool_env("DELETE_AFTER_UPLOAD", True)

    startup_scan_enabled: bool = _bool_env("STARTUP_SCAN_ENABLED", True)
