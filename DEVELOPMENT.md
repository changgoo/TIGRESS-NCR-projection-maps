# Development Log

Entries are newest-first.

---

## 2026-03-25 — Model name mapping (28 paper models)

### Added
- `map_model_names.py` — parses beta, Z_gas, Z_dust, and Sigma_0 from folder basenames using regex; replicates `LowZData.get_model_name()` without loading simulation data. Writes `model_name_mapping.md`.
- `model_name_mapping.md` — basename → model name table for the 28 models in Table 2 of arXiv:2405.19227, sorted by ascending Sigma_0, ascending beta, then descending Z_gas.

### Filtering logic (applied in order)
1. Skip folders with missing beta or Z parameters
2. Skip Z=0.01 runs (not in paper)
3. Skip early evolution runs — non-`xy` folders that have an `xy` counterpart (iCR4↔iCR5 substitution also checked)
4. Hardcoded skip list: two LGR4-b10 runs without `xy` counterpart, one `SBZ002_V00` variant

### Sigma_0 assignment
- Parsed from `_SXX` tag when present (S05=5, S30=30, S100=100, S150=150)
- Defaults: R8 → 12, LGR4 → 50

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
