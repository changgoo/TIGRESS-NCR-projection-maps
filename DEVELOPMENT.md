# Development Log

Entries are newest-first.

---

## 2026-03-27 — Move copy-related scripts to test/; script/ now analysis-only

### Changed
- `script/` now contains only `loadsim.py` (data analysis).
- `copy_data.sh`, `extract_athinput.sh`, `update_data_readme.sh`, `map_model_names.py`,
  and `model_name_mapping.md` moved from `script/` to `test/`.
- `test/conftest.py`: updated sys.path to add `test/` (was `script/`).

---

## 2026-03-27 — Reorganise repo: move scripts to script/, tests to test/

### Changed
- Moved `copy_data.sh`, `extract_athinput.sh`, `update_data_readme.sh`, `map_model_names.py`,
  and `model_name_mapping.md` from the repo root into `script/`.
- Moved `test_map_model_names.py` into `test/`; added `test/conftest.py` to put `script/` on sys.path.
- Updated `REPO_DIR` logic in all three shell scripts: each now sets `SCRIPT_DIR` to the script's
  own directory and `REPO_DIR` to its parent (the repo root), so `data/` references remain correct.
- `copy_data.sh` now resolves sibling scripts via `${SCRIPT_DIR}` instead of `${REPO_DIR}`.

---

## 2026-03-27 — Add high-resolution models R8-4pc and LGR4-2pc

### Changed
- `map_model_names.py`: added `EXTRA_MODELS` dict mapping two higher-resolution run basenames
  (`R8_4pc_NCR.full.xy2048.eps0.np768.has` → `R8-4pc`,
   `LGR4_2pc_NCR.full.xy1024.eps1.e-8.np768` → `LGR4-2pc`) from
  Kim et al. (2023, ApJ 946 3).  `lookup()` checks this dict before any
  directory listing, so these models pass through `copy_data.sh` without
  needing the standard beta/Z naming convention.
- `test_map_model_names.py`: new pytest file covering `parse_params`, `get_model_name`,
  `EXTRA_MODELS`, and `lookup` (12 tests, all pass).

---

## 2026-03-25 — Exclude starpar/ from git

### Changed
- `.gitignore`: added `data/*/starpar/` alongside `data/*/prj/`; only `hst/` (thinned `.hst` + `.sn`) is now git-tracked.
- `update_data_readme.sh`: `starpar` no longer counted in Git total; column header updated to `starpar (local)`.
- `copy_data.sh`: per-model README now marks `starpar/` as not in git (`—`).
- `README.md`, `CLAUDE.md`: updated notes to reflect that both `prj/` and `starpar/` must be downloaded separately.
- Result: git-tracked data reduced to **1.1 GB** (hst only, down from 3.0 GB).

---

## 2026-03-25 — Thin .hst files by factor 10 to fit GitHub limits

### Changed
- `copy_data.sh`: `hst/` copy no longer uses rsync; instead, `.hst` files are thinned by a factor of 10 with `awk 'NR<=3 || (NR-3)%10==1'` (preserves 3 header lines, keeps every 10th data row). `.sn` files are still copied verbatim (event-based, cannot thin). `phase*.hst` and `whole.hst` continue to be excluded.
- All 28 existing `data/*/hst/*.hst` files re-processed in-place with the same awk rule.
- Result: max `.hst` file 89 MB (under GitHub 100 MB hard limit); total git-tracked data 3.0 GB (down from ~5.5 GB).

---

## 2026-03-25 — Finalize data layout and documentation

### Changed
- `copy_data.sh`: destination folder is now the short paper model name (e.g. `R8-b1-Z1.0`) resolved via `map_model_names.py --lookup`; exits with error if the run is not a recognised paper model.
- `copy_data.sh`: `prj/` is now copied in full (all snapshots); excluded from git via `.gitignore` (`data/*/prj/`).
- `README.md`: added Models section with the 28-model table (Sigma_0, beta, Z_gas, Z_dust), paper reference (arXiv:2405.19227), and note that `prj/` must be downloaded separately.
- `CLAUDE.md`: updated directory conventions and data copy script description to reflect model-name folders and `prj/` gitignore.

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
