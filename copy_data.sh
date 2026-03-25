#!/usr/bin/env bash
# copy_data.sh — Copy processed simulation results to data/_basename_/
#
# Usage: ./copy_data.sh <base_dir> [full_data_url]
#
# Copies prj/, starpar/, and hst/ from <base_dir> into
# data/<basename>/ relative to this script's location, then writes
# a summary README.md and extracts athinput.runtime.
#
# Subset rules:
#   prj/    — all files (large; excluded from git via .gitignore)
#   hst/    — only *.hst and *.sn; excludes *.p, phase*.hst, whole.hst
#   starpar/ — all files

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <base_dir> [full_data_url]" >&2
    exit 1
fi

BASE_DIR="$(realpath "${1%/}")"
BASENAME="$(basename "$BASE_DIR")"
FULL_DATA_URL="${2:-}"

# Resolve destination folder name: use paper model name when available,
# fall back to basename with a warning.
MODEL_NAME=$(python3 "${REPO_DIR}/map_model_names.py" --lookup "${BASENAME}" 2>/dev/null || true)
if [[ -z "$MODEL_NAME" ]]; then
    echo "Error: '${BASENAME}' is not a recognised paper model. Skipping." >&2
    exit 1
fi
DEST="${REPO_DIR}/data/${MODEL_NAME}"

echo "Source : ${BASE_DIR}"
echo "Dest   : ${DEST}"
echo ""

mkdir -p "${DEST}"

# ── Copy each subdirectory ────────────────────────────────────────────────────
declare -A ORIG_FILES ORIG_SIZE REPO_FILES REPO_SIZE

for subdir in prj starpar hst; do
    SRC="${BASE_DIR}/${subdir}"
    if [[ -d "$SRC" ]]; then
        # Original counts (source)
        ORIG_FILES[$subdir]=$(find "$SRC" -type f | wc -l)
        ORIG_SIZE[$subdir]=$(du -sb "$SRC" | awk '{print $1}')

        echo "Copying ${subdir}/ ..."
        if [[ "$subdir" == "prj" ]]; then
            # Copy all projection files (excluded from git via .gitignore)
            rsync -a --info=progress2 "${SRC}/" "${DEST}/${subdir}/"
        elif [[ "$subdir" == "hst" ]]; then
            # Exclude reproducible pickle files and bulky phase/whole histories.
            # .hst files are thinned by factor 10 (keep every 10th data row);
            # .sn files are event-based and copied verbatim.
            mkdir -p "${DEST}/${subdir}/"
            for f in "${SRC}"/*.hst; do
                [[ -f "$f" ]] || continue
                fname="$(basename "$f")"
                # skip phase and whole history files
                [[ "$fname" == *.phase*.hst ]] && continue
                [[ "$fname" == *.whole.hst  ]] && continue
                awk 'NR<=3 || (NR-3)%10==1' "$f" > "${DEST}/${subdir}/${fname}"
            done
            for f in "${SRC}"/*.sn; do
                [[ -f "$f" ]] || continue
                cp "$f" "${DEST}/${subdir}/"
            done
        else
            rsync -a --info=progress2 "${SRC}/" "${DEST}/${subdir}/"
        fi

        REPO_FILES[$subdir]=$(find "${DEST}/${subdir}" -type f | wc -l)
        REPO_SIZE[$subdir]=$(du -sb "${DEST}/${subdir}" | awk '{print $1}')
        echo "  done: ${REPO_FILES[$subdir]} files, $(numfmt --to=iec "${REPO_SIZE[$subdir]}")"
    else
        echo "  Warning: ${SRC} not found, skipping."
        ORIG_FILES[$subdir]=0; ORIG_SIZE[$subdir]=0
        REPO_FILES[$subdir]=0; REPO_SIZE[$subdir]=0
    fi
    echo ""
done

# ── Totals ────────────────────────────────────────────────────────────────────
TOTAL_ORIG_FILES=0; TOTAL_ORIG_BYTES=0
TOTAL_REPO_FILES=0; TOTAL_REPO_BYTES=0
for subdir in prj starpar hst; do
    TOTAL_ORIG_FILES=$(( TOTAL_ORIG_FILES + ORIG_FILES[$subdir] ))
    TOTAL_ORIG_BYTES=$(( TOTAL_ORIG_BYTES + ORIG_SIZE[$subdir] ))
    TOTAL_REPO_FILES=$(( TOTAL_REPO_FILES + REPO_FILES[$subdir] ))
    TOTAL_REPO_BYTES=$(( TOTAL_REPO_BYTES + REPO_SIZE[$subdir] ))
done

# ── Write README.md ───────────────────────────────────────────────────────────
README="${DEST}/README.md"
{
    echo "# Data: ${BASENAME}"
    echo ""
    echo "- **Source:** \`${BASE_DIR}\`"
    echo "- **Copied:** $(date -u '+%Y-%m-%d %H:%M UTC')"
    if [[ -n "$FULL_DATA_URL" ]]; then
        echo "- **Full dataset:** ${FULL_DATA_URL}"
    else
        echo "- **Full dataset:** TBD"
    fi
    echo ""
    echo "## Contents"
    echo ""
    echo "| Folder | Source files | Source size | Local files | Local size | In git | Notes |"
    echo "|--------|-------------:|------------:|------------:|-----------:|:------:|-------|"
    for subdir in prj starpar hst; do
        if (( ORIG_FILES[$subdir] > 0 )); then
            case "$subdir" in
                prj)     note="all snapshots"; ingit="—" ;;
                hst)     note="\`.hst\` (thinned 10×) and \`.sn\`"; ingit="✓" ;;
                starpar) note="all files"; ingit="—" ;;
            esac
            echo "| \`${subdir}/\` | ${ORIG_FILES[$subdir]} | $(numfmt --to=iec "${ORIG_SIZE[$subdir]}") | ${REPO_FILES[$subdir]} | $(numfmt --to=iec "${REPO_SIZE[$subdir]}") | ${ingit} | ${note} |"
        fi
    done
    echo ""
    echo "**Total (local):** ${TOTAL_REPO_FILES} files, $(numfmt --to=iec "$TOTAL_REPO_BYTES")"
    echo ""
    echo "**Total (source):** ${TOTAL_ORIG_FILES} files, $(numfmt --to=iec "$TOTAL_ORIG_BYTES")"
} > "$README"

echo "Summary written to: ${README}"
echo "Repo total : ${TOTAL_REPO_FILES} files, $(numfmt --to=iec "$TOTAL_REPO_BYTES")"
echo "Orig total : ${TOTAL_ORIG_FILES} files, $(numfmt --to=iec "$TOTAL_ORIG_BYTES")"
echo ""

# ── Extract athinput.runtime ──────────────────────────────────────────────────
"${REPO_DIR}/extract_athinput.sh" "${BASE_DIR}" "${DEST}"

# ── Regenerate data/README.md ─────────────────────────────────────────────────
"${REPO_DIR}/update_data_readme.sh"
