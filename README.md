# TIGRESS-NCR Projection Maps

A curated copy of processed results from TIGRESS-NCR simulations, together with scripts to read and analyze the data.

## Repository Structure

```
.
├── data/                   # Simulation data, organized by run basename
│   └── _basename_/
│       ├── prj/            # Projection maps
│       ├── starpar/        # Star particle outputs
│       ├── hst/            # History (time series) outputs
│       └── README.md       # Data summary (file count, size, run metadata)
├── script/                 # Python analysis scripts
└── DEVELOPMENT.md          # Development log (latest to first)
```

## Data

Each simulation run's data lives under `data/_basename_/`, where `_basename_` is derived from the base directory path of the original simulation output. Each data directory contains a `README.md` with a summary of the copied files and the parsed runtime parameters (`athinput.runtime`).

## Dependencies

Python scripts rely on [pyathena](https://github.com/jeonggyukim/pyathena). Install it with:

```bash
pip install git+https://github.com/jeonggyukim/pyathena.git
```

or clone and install in editable mode:

```bash
git clone https://github.com/jeonggyukim/pyathena.git
cd pyathena
pip install -e .
```

## Scripts

See `script/` for analysis scripts. Each script has a corresponding test. Run tests with:

```bash
pytest script/
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for a log of major changes.
