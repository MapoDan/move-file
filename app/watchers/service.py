from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.core.config import Settings
from app.core.state import ProcessedState
from app.watchers.router import HandlerRouter

logger = logging.getLogger("watcher")


class Mp3EventHandler(FileSystemEventHandler):
    def __init__(self, settings: Settings, state: ProcessedState, router: HandlerRouter) -> None:
        self.settings = settings
        self.state = state
        self.router = router

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._handle_candidate(Path(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._handle_candidate(Path(event.dest_path))

    def _handle_candidate(self, file_path: Path) -> None:
        if file_path.suffix.lower() != ".mp3":
            return
        if file_path.name.startswith(".") or file_path.name.endswith((".tmp", ".part")):
            return
        thread = threading.Thread(target=self._process_file, args=(file_path,), daemon=True)
        thread.start()

    def _process_file(self, file_path: Path) -> None:
        source_dir, handler = self.router.resolve(file_path)
        if not handler:
            return
        if self.state.is_processed(str(file_path)):
            return
        if not wait_for_stable_size(file_path, self.settings.stability_seconds, self.settings.stability_poll_seconds):
            return

        for attempt in range(1, self.settings.max_retries + 1):
            try:
                handler.handle(file_path, self.settings)
                self.state.mark_processed(str(file_path), str(source_dir), handler.name)
                logger.info(
                    "file processed",
                    extra={"source_dir": str(source_dir), "file": str(file_path), "handler": handler.name, "attempt": attempt},
                )
                return
            except Exception:
                logger.exception(
                    "file processing failed",
                    extra={"source_dir": str(source_dir), "file": str(file_path), "handler": handler.name, "attempt": attempt},
                )
                time.sleep(self.settings.retry_delay_seconds)


def wait_for_stable_size(path: Path, stable_seconds: int, poll_seconds: int) -> bool:
    unchanged_for = 0
    last_size = -1
    while unchanged_for < stable_seconds:
        if not path.exists():
            return False
        size = path.stat().st_size
        if size == last_size:
            unchanged_for += poll_seconds
        else:
            unchanged_for = 0
            last_size = size
        time.sleep(poll_seconds)
    return True


class WatcherService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.observer = Observer()

    def run(self) -> None:
        state = ProcessedState(self.settings.processed_db_path)
        router = HandlerRouter(self.settings)
        handler = Mp3EventHandler(self.settings, state, router)

        for watch_dir in (self.settings.input_dir, self.settings.dir_clean, self.settings.dir_tagged):
            Path(watch_dir).mkdir(parents=True, exist_ok=True)
            self.observer.schedule(handler, watch_dir, recursive=self.settings.recursive_watch)
            logger.info("watch registered", extra={"source_dir": watch_dir})

        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.observer.stop()
            self.observer.join()
