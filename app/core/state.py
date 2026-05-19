from __future__ import annotations

import sqlite3
from pathlib import Path


class ProcessedState:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

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
