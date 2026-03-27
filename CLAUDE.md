# CLAUDE.md — Guidelines for AI Assistance

## Project Purpose

This repository stores processed outputs from TIGRESS-NCR galaxy simulations and Python scripts to read and analyze them. Scripts are developed interactively with the user.

## Directory Conventions

- `data/<model>/` — simulation data copied from original paths; `<model>` is the short paper model name (e.g. `R8-b1-Z1.0`) resolved by `test/map_model_names.py`. The 28 models from Table 2 of arXiv:2405.19227 plus two high-resolution models (`R8-4pc`, `LGR4-2pc` from 2023ApJ...946....3K) are accepted; `copy_data.sh` exits with an error for anything else.
  - Subfolders: `prj/`, `starpar/`, `hst/`
  - All of `data/` is excluded from git via `.gitignore`
  - Each run directory contains `README.md` (data summary) and `athinput.runtime` (parsed runtime parameters)
- `script/` — Python analysis scripts only (e.g. `loadsim.py`)
- `test/` — pytest tests and data-management utilities (`copy_data.sh`, `extract_athinput.sh`, `update_data_readme.sh`, `map_model_names.py`, `sync_data.sh`)
- `DEVELOPMENT.md` — development log, newest entries first

## Coding Conventions

- **Language:** Python for analysis scripts; shell (bash/awk/sed) for data-management utilities.
- **Dependencies:** [pyathena](https://github.com/jeonggyukim/pyathena) is the primary analysis library.
- **Tests:** Every script must have a corresponding test. Use `pytest`.
- **Running tests:** `module load anaconda3/2024.6 && conda run -n pyathena python -m pytest test/`
- **Documentation:** Update `DEVELOPMENT.md` (latest-to-first) after each major milestone.

## Data Scripts (in `test/`)

- `copy_data.sh <base_dir>` — resolves the model name via `map_model_names.py --lookup`; exits with error if the run is not a recognised model.
  - Copies all files in `prj/` and `starpar/`, and thinned `.hst` + verbatim `.sn` from `hst/`.
  - Calls `extract_athinput.sh` to parse the PAR_DUMP block from the latest `out*.txt` and save it as `athinput.runtime`.
  - Logs original vs. repo file counts and sizes to `data/<model>/README.md`.
- `sync_data.sh [extra rsync flags]` — rsyncs `data/` to `/tigerdata/EOSTRIKE/TIGRESS-NCR/TIGRESS-NCR-projection-maps/data/`.
  - Excludes `*.p` files outside `prj/` and deletes them at the destination.
  - Uses `--whole-file --inplace` required by the tigerdata storage backend.
  - Pass `--dry-run` to preview without transferring.

## Workflow Notes

- Scripts are developed incrementally through conversation with the user. Do not add features beyond what is explicitly requested.
- Always write tests before or alongside new functionality.
- Keep solutions simple; avoid premature abstractions.
