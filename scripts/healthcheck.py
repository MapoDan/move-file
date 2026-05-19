from pathlib import Path
import os
import sys

required = [
    os.getenv("INPUT_DIR", "/data/input"),
    os.getenv("DIR_CLEAN", "/data/clean"),
    os.getenv("DIR_TAGGED", "/data/tagged"),
    str(Path(os.getenv("PROCESSED_DB_PATH", "/data/state/processed.sqlite3")).parent),
]

ok = all(Path(p).exists() for p in required)
sys.exit(0 if ok else 1)
