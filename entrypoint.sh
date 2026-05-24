#!/usr/bin/env sh
set -eu

mkdir -p "${INPUT_DIR:-/data/input}" "${DIR_CLEAN:-/data/clean}" "${DIR_TAGGED:-/data/tagged}"
STATE_DB_PATH="${PROCESSED_DB_PATH:-/data/state/processed.sqlite3}"
STATE_DIR="$(dirname "$STATE_DB_PATH")"
mkdir -p "$STATE_DIR"

if [ ! -w "$STATE_DIR" ]; then
  echo "[WARN] State dir '$STATE_DIR' is not writable by container user; using /tmp/processed.sqlite3" >&2
  export PROCESSED_DB_PATH=/tmp/processed.sqlite3
fi

exec python -m app.main
