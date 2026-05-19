from __future__ import annotations

from app.core.config import Settings
from app.core.logging_config import configure_logging
from app.watchers.service import WatcherService


def main() -> None:
    settings = Settings()
    configure_logging(settings.log_level)
    WatcherService(settings).run()


if __name__ == "__main__":
    main()
