# Development Log

Entries are newest-first.

---

## 2026-03-25 — Reduce prj/ footprint and add original-vs-repo stats to README

### Changed
- `copy_data.sh`: `prj/` now only copies snapshots whose index ends in `00` (every 100th step) via rsync filter `--include='*00.p' --exclude='*'`.
  - Result for `LGR4_4pc_NCR.*`: `prj/` reduced from 701 files / 2.3 G → 8 files / 27 M.
- `copy_data.sh`: accepts an optional second argument `[full_data_url]` for the location of the complete dataset (e.g., Zenodo/Globus); written into the per-run README as "Full dataset". Defaults to "TBD".
- `copy_data.sh`: README now tracks both original (source) and repo (copied) file counts and sizes per subfolder in a single table.
- Overall repo footprint for `LGR4_4pc_NCR.*`: 782 files, 182 M (down from 1,516 files, 4.3 G).

---

## 2026-03-25 — Reduce hst/ footprint for GitHub sharing

### Changed
- `copy_data.sh`: `hst/` is now copied with rsync filter rules to keep only files suitable for sharing:
  - **Excluded:** `*.p` (reproducible pickle caches), `*.phase*.hst`, `*.whole.hst`
  - **Included:** `*.hst` (main history file only), `*.sn`
  - Result for `LGR4_4pc_NCR.*`: `hst/` reduced from 2.0 G → 79 M (2 files).

---

## 2026-03-25 — Initial setup and data copy scripts

### Added
- `copy_data.sh` — copies `prj/`, `starpar/`, and `hst/` from a simulation base directory into `data/_basename_/` using `rsync`. Writes a summary table (file counts, sizes per subfolder, total) to `data/_basename_/README.md`. Calls `extract_athinput.sh` automatically on completion.
- `extract_athinput.sh` — finds all `out*.txt` files in the simulation directory, sorted newest-first, and extracts the PAR_DUMP block (text between the two `# -+ PAR_DUMP -+` marker lines) using `awk`. Saves result to `data/_basename_/athinput.runtime`.
- `README.md` — repository overview: structure, data layout, pyathena dependency, test instructions.
- `CLAUDE.md` — AI assistant guidelines: conventions, data copy behavior, coding standards.

### Tested on
- `LGR4_4pc_NCR.full.b10.v3.iCR4.Zg1.Zd1.xy1024.eps1.e-8`: 1,516 files, 4.3 G copied; `athinput.runtime` extracted from `out.r3.txt` (286 lines).
