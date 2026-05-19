from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger("state")


class ProcessedState:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_parent_dir(self.db_path)
        self._init_db_with_fallback()

    def _ensure_parent_dir(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db_with_fallback(self) -> None:
        try:
            self._init_db()
        except sqlite3.OperationalError:
            fallback_path = "/tmp/processed.sqlite3"
            logger.exception(
                "unable to initialize sqlite state db, falling back to /tmp",
                extra={"file": self.db_path},
            )
            self.db_path = fallback_path
            self._ensure_parent_dir(self.db_path)
            self._init_db()
            logger.warning(
                "sqlite fallback enabled; processed-state persistence is ephemeral unless volume permissions are fixed",
                extra={"file": self.db_path},
            )

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_files (
                    file_path TEXT PRIMARY KEY,
                    source_dir TEXT NOT NULL,
                    script_name TEXT NOT NULL,
                    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def is_processed(self, file_path: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_files WHERE file_path = ?", (file_path,)
            ).fetchone()
            return row is not None

    def mark_processed(self, file_path: str, source_dir: str, script_name: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO processed_files (file_path, source_dir, script_name) VALUES (?, ?, ?)",
                (file_path, source_dir, script_name),
            )
