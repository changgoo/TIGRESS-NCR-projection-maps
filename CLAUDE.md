# CLAUDE.md — Guidelines for AI Assistance

## Project Purpose

This repository stores processed outputs from TIGRESS-NCR galaxy simulations and Python scripts to read and analyze them. Scripts are developed interactively with the user.

## Directory Conventions

- `data/<model>/` — simulation data copied from original paths; `<model>` is the short paper model name (e.g. `R8-b1-Z1.0`) resolved by `map_model_names.py`. Only the 28 models from Table 2 of arXiv:2405.19227 are accepted; `copy_data.sh` exits with an error for anything else.
  - Subfolders: `prj/`, `starpar/`, `hst/`
  - `prj/` contains the full projection data and is excluded from git via `.gitignore`
  - Each run directory contains `README.md` (data summary) and `athinput.runtime` (parsed runtime parameters)
- `script/` — Python analysis scripts
- `DEVELOPMENT.md` — development log, newest entries first

## Coding Conventions

- **Language:** Python for analysis scripts; shell (bash/awk/sed) for data-management utilities.
- **Dependencies:** [pyathena](https://github.com/jeonggyukim/pyathena) is the primary analysis library.
- **Tests:** Every script must have a corresponding test. Use `pytest`.
- **Documentation:** Update `DEVELOPMENT.md` (latest-to-first) after each major milestone.

## Data Copy Script

- `copy_data.sh <base_dir>` — resolves the model name via `map_model_names.py --lookup`; exits with error if the run is not a paper model.
- Copies all files in `prj/` (gitignored), `starpar/` (all), and `hst/` (`.hst` and `.sn` only).
- Calls `extract_athinput.sh` to parse the PAR_DUMP block from the latest `out*.txt` and save it as `athinput.runtime`.
- Logs original vs. repo file counts and sizes to `data/<model>/README.md`.

## Workflow Notes

- Scripts are developed incrementally through conversation with the user. Do not add features beyond what is explicitly requested.
- Always write tests before or alongside new functionality.
- Keep solutions simple; avoid premature abstractions.
