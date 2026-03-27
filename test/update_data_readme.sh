#!/usr/bin/env bash
# update_data_readme.sh — Regenerate data/README.md with a per-model size summary.
#
# Usage: ./update_data_readme.sh
#
# Scans every subdirectory under data/, computes file counts and sizes for
# prj/, starpar/, and hst/, and writes a summary table to data/README.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${REPO_DIR}/data"
README="${DATA_DIR}/README.md"

# ── Collect per-model stats ───────────────────────────────────────────────────
declare -a MODELS
declare -A M_PRJ_FILES M_PRJ_SIZE
declare -A M_STARPAR_FILES M_STARPAR_SIZE
declare -A M_HST_FILES M_HST_SIZE
declare -A M_OTHER_SIZE

for model_dir in "${DATA_DIR}"/*/; do
    [[ -d "$model_dir" ]] || continue
    model="$(basename "$model_dir")"
    MODELS+=("$model")

    for subdir in prj starpar hst; do
        d="${model_dir}${subdir}"
        if [[ -d "$d" ]]; then
            n=$(find "$d" -type f | wc -l)
            s=$(du -sb "$d" | awk '{print $1}')
        else
            n=0; s=0
        fi
        case "$subdir" in
            prj)     M_PRJ_FILES[$model]=$n;     M_PRJ_SIZE[$model]=$s ;;
            starpar) M_STARPAR_FILES[$model]=$n; M_STARPAR_SIZE[$model]=$s ;;
            hst)     M_HST_FILES[$model]=$n;     M_HST_SIZE[$model]=$s ;;
        esac
    done

    # Other files (athinput.runtime, README.md)
    M_OTHER_SIZE[$model]=$(find "$model_dir" -maxdepth 1 -type f -exec du -sb {} + \
                           | awk '{sum+=$1} END{print sum+0}')
done

# ── Grand totals ──────────────────────────────────────────────────────────────
GRAND_PRJ=0; GRAND_STARPAR=0; GRAND_GIT=0; GRAND_LOCAL=0
for model in "${MODELS[@]}"; do
    git_bytes=$(( M_HST_SIZE[$model] + M_OTHER_SIZE[$model] ))
    local_bytes=$(( git_bytes + M_PRJ_SIZE[$model] + M_STARPAR_SIZE[$model] ))
    GRAND_PRJ=$(( GRAND_PRJ + M_PRJ_SIZE[$model] ))
    GRAND_STARPAR=$(( GRAND_STARPAR + M_STARPAR_SIZE[$model] ))
    GRAND_GIT=$(( GRAND_GIT + git_bytes ))
    GRAND_LOCAL=$(( GRAND_LOCAL + local_bytes ))
done

# ── Write README.md ───────────────────────────────────────────────────────────
{
    echo "# Data Summary"
    echo ""
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M UTC')"
    echo ""
    echo "| Model | starpar (local) | hst | prj (local) | Git total | Local total |"
    echo "|-------|----------------:|----:|------------:|----------:|------------:|"
    for model in "${MODELS[@]}"; do
        git_bytes=$(( M_HST_SIZE[$model] + M_OTHER_SIZE[$model] ))
        local_bytes=$(( git_bytes + M_PRJ_SIZE[$model] + M_STARPAR_SIZE[$model] ))
        printf "| %-30s | %s (%d) | %s (%d) | %s (%d) | %s | %s |\n" \
            "$model" \
            "$(numfmt --to=iec "${M_STARPAR_SIZE[$model]}")" "${M_STARPAR_FILES[$model]}" \
            "$(numfmt --to=iec "${M_HST_SIZE[$model]}")"     "${M_HST_FILES[$model]}" \
            "$(numfmt --to=iec "${M_PRJ_SIZE[$model]}")"     "${M_PRJ_FILES[$model]}" \
            "$(numfmt --to=iec "$git_bytes")" \
            "$(numfmt --to=iec "$local_bytes")"
    done
    echo "| **Total** | $(numfmt --to=iec "$GRAND_STARPAR") | | $(numfmt --to=iec "$GRAND_PRJ") | **$(numfmt --to=iec "$GRAND_GIT")** | $(numfmt --to=iec "$GRAND_LOCAL") |"
} > "$README"

echo "Written to ${README}"
