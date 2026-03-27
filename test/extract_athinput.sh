#!/usr/bin/env bash
# extract_athinput.sh — Extract the PAR_DUMP block from out*.txt files
#
# Usage: ./extract_athinput.sh <base_dir> [dest_dir]
#
# Searches for out*.txt files in <base_dir>, sorted newest-first,
# and extracts the text between the two PAR_DUMP marker lines from
# the first (latest) file that contains the block.
# Output is saved to <dest_dir>/athinput.runtime  (default: data/<basename>/).
#
# The PAR_DUMP marker pattern (both opening and closing lines match):
#   # --------------------- PAR_DUMP -+

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <base_dir> [dest_dir]" >&2
    exit 1
fi

BASE_DIR="$(realpath "${1%/}")"
BASENAME="$(basename "$BASE_DIR")"
DEST_DIR="${2:-${REPO_DIR}/data/${BASENAME}}"
OUTPUT="${DEST_DIR}/athinput.runtime"

mkdir -p "${DEST_DIR}"

# ── Find out*.txt files, newest first ────────────────────────────────────────
# Use find + sort by modification time via -printf %T@
mapfile -t OUT_FILES < <(
    find "${BASE_DIR}" -maxdepth 1 -name "out*.txt" -printf '%T@ %p\n' \
    | sort -rn \
    | awk '{print $2}'
)

if [[ ${#OUT_FILES[@]} -eq 0 ]]; then
    echo "Error: no out*.txt files found in ${BASE_DIR}" >&2
    exit 1
fi

echo "Found ${#OUT_FILES[@]} out*.txt file(s) in ${BASE_DIR}"

# ── Extract PAR_DUMP block from the newest file that has one ─────────────────
for f in "${OUT_FILES[@]}"; do
    if grep -qE "^# -+ PAR_DUMP -+" "$f"; then
        echo "Extracting PAR_DUMP from: $(basename "$f")"
        awk '
            /^# -+ PAR_DUMP -+/ {
                count++
                print
                if (count == 2) exit
                next
            }
            count == 1 { print }
        ' "$f" > "${OUTPUT}"
        echo "Saved to: ${OUTPUT}"
        exit 0
    fi
done

echo "Error: no out*.txt file in ${BASE_DIR} contains a PAR_DUMP block." >&2
exit 1
