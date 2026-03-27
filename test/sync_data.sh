#!/usr/bin/env bash
# sync_data.sh — Sync data/ and DATA_SUMMARY.md to the tigerdata archive.
#
# Copies all files under data/ to the canonical archive path, excluding
# *.p files that are NOT inside a prj/ subdirectory.  Any such excluded
# *.p files already present at the destination are deleted.
# Also copies DATA_SUMMARY.md to the archive root.
#
# Usage: ./sync_data.sh [extra rsync flags]
#   e.g. ./sync_data.sh --dry-run
#        ./sync_data.sh -n          (same, short form)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

ARCHIVE="/tigerdata/EOSTRIKE/TIGRESS-NCR/TIGRESS-NCR-projection-maps"

rsync -av \
    --whole-file --inplace \
    --filter='+ */prj/' \
    --filter='+ */prj/*.p' \
    --filter='- *.p' \
    --delete-excluded \
    "$@" \
    "${REPO_DIR}/data/" "${ARCHIVE}/data/"

rsync -av --whole-file --inplace \
    "$@" \
    "${REPO_DIR}/DATA_SUMMARY.md" "${ARCHIVE}/"
