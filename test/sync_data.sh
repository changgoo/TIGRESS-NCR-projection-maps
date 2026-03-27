#!/usr/bin/env bash
# sync_data.sh — Sync data/ to the tigerdata archive.
#
# Copies all files under data/ to the canonical archive path, excluding
# *.p files that are NOT inside a prj/ subdirectory.  Any such excluded
# *.p files already present at the destination are deleted.
#
# Usage: ./sync_data.sh [extra rsync flags]
#   e.g. ./sync_data.sh --dry-run
#        ./sync_data.sh -n          (same, short form)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

SRC="${REPO_DIR}/data/"
DEST="/tigerdata/EOSTRIKE/TIGRESS-NCR/TIGRESS-NCR-projection-maps/data/"

rsync -av \
    --whole-file --inplace \
    --filter='+ */prj/' \
    --filter='+ */prj/*.p' \
    --filter='- *.p' \
    --delete-excluded \
    "$@" \
    "$SRC" "$DEST"
