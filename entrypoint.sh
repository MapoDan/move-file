#!/usr/bin/env sh
set -eu

mkdir -p "${INPUT_DIR:-/data/input}" "${DIR_CLEAN:-/data/clean}" "${DIR_TAGGED:-/data/tagged}"
mkdir -p "$(dirname "${PROCESSED_DB_PATH:-/data/state/processed.sqlite3}")"

exec python -m app.main
