# CLAUDE.md — Guidelines for AI Assistance

## Project Purpose

This repository stores processed outputs from TIGRESS-NCR galaxy simulations and Python scripts to read and analyze them. Scripts are developed interactively with the user.

## Directory Conventions

- `data/_basename_/` — simulation data copied from original paths; `_basename_` is derived from the base simulation directory path.
  - Subfolders: `prj/`, `starpar/`, `hst/`
  - Each run directory contains `README.md` (data summary) and `athinput.runtime` (parsed runtime parameters)
- `script/` — Python analysis scripts
- `DEVELOPMENT.md` — development log, newest entries first

## Coding Conventions

- **Language:** Python for analysis scripts; shell (bash/awk/sed) for data-management utilities.
- **Dependencies:** [pyathena](https://github.com/jeonggyukim/pyathena) is the primary analysis library.
- **Tests:** Every script must have a corresponding test. Use `pytest`.
- **Documentation:** Update `DEVELOPMENT.md` (latest-to-first) after each major milestone.

## Data Copy Script

- Reads `out*.txt` files in the simulation directory.
- Parses the block between `# --------------------- PAR_DUMP -----------------------` lines and saves it to `athinput.runtime`.
- If multiple `out*.txt` files exist, use the latest one that contains the PAR_DUMP block.
- Logs a summary (number of files, total size) to `data/_basename_/README.md`.

## Workflow Notes

- Scripts are developed incrementally through conversation with the user. Do not add features beyond what is explicitly requested.
- Always write tests before or alongside new functionality.
- Keep solutions simple; avoid premature abstractions.
