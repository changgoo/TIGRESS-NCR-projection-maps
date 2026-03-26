# TIGRESS-NCR Projection Maps

A curated copy of processed results from TIGRESS-NCR simulations, together with scripts to read and analyze the data.

## Repository Structure

```
.
├── data/                   # Simulation data, organized by model name
│   └── _model_/
│       ├── prj/            # Projection maps (*not* in repo — download separately)
│       ├── starpar/        # Star particle outputs (*not* in repo — download separately)
│       ├── hst/            # History (time series) outputs
│       └── README.md       # Data summary (file count, size, run metadata)
├── notebook/               # Example Jupyter notebooks
├── script/                 # Python analysis scripts
└── DEVELOPMENT.md          # Development log (latest to first)
```

## Data

Each simulation run's data lives under `data/<model>/`, where `<model>` is the short model name (e.g. `R8-b1-Z1.0`). Each data directory contains a `README.md` with a summary of the copied files and the parsed runtime parameters (`athinput.runtime`).

> **Note:** The `prj/` (projection maps) and `starpar/` (star particle outputs) subdirectories are **not included in this repository** due to their size. They must be downloaded separately — see each `data/<model>/README.md` for the full dataset location once available.

### Models

The 28 models below are those used in [Kim, Ostriker, et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...972...67K/abstract) and listed in Table 2 of that paper. `Sigma0` is the initial gas surface density [M☉/pc²]; `beta` is the initial plasma beta; `Z_gas` and `Z_dust` are gas- and dust-phase metallicities relative to solar.

| model | Sigma0 | beta | Z_gas | Z_dust |
|-------|-------:|-----:|------:|-------:|
| S05-Z1.0 | 5 | 10 | 1.0 | 1.0 |
| S05-Z0.1 | 5 | 10 | 0.1 | 0.1 |
| R8-b1-Z3.0 | 12 | 1 | 3.0 | 3.0 |
| R8-b1-Z1.0 | 12 | 1 | 1.0 | 1.0 |
| R8-b1-Z0.3 | 12 | 1 | 0.3 | 0.3 |
| R8-b1-Zg0.1Zd0.025 | 12 | 1 | 0.1 | 0.025 |
| R8-b1-Z0.1 | 12 | 1 | 0.1 | 0.1 |
| R8-b10-Z1.0 | 12 | 10 | 1.0 | 1.0 |
| R8-b10-Z0.3 | 12 | 10 | 0.3 | 0.3 |
| R8-b10-Zg0.1Zd0.025 | 12 | 10 | 0.1 | 0.025 |
| R8-b10-Z0.1 | 12 | 10 | 0.1 | 0.1 |
| S30-Z1.0 | 30 | 1 | 1.0 | 1.0 |
| S30-Z0.1 | 30 | 1 | 0.1 | 0.1 |
| LGR4-b1-Z3.0 | 50 | 1 | 3.0 | 3.0 |
| LGR4-b1-Z1.0 | 50 | 1 | 1.0 | 1.0 |
| LGR4-b1-Z0.3 | 50 | 1 | 0.3 | 0.3 |
| LGR4-b1-Zg0.1Zd0.025 | 50 | 1 | 0.1 | 0.025 |
| LGR4-b1-Z0.1 | 50 | 1 | 0.1 | 0.1 |
| LGR4-b10-Z1.0 | 50 | 10 | 1.0 | 1.0 |
| LGR4-b10-Z0.1 | 50 | 10 | 0.1 | 0.1 |
| S100-Z1.0 | 100 | 1 | 1.0 | 1.0 |
| S100-Z1.0r | 100 | 1 | 1.0 | 1.0 |
| S100-Z0.1 | 100 | 1 | 0.1 | 0.1 |
| S150-Om100q0-Z1.0 | 150 | 2 | 1.0 | 1.0 |
| S150-Om200-Z1.0 | 150 | 2 | 1.0 | 1.0 |
| S150-Om200-Z1.0r | 150 | 2 | 1.0 | 1.0 |
| S150-Om100q0-Z0.1 | 150 | 2 | 0.1 | 0.1 |
| S150-Om200-Z0.1 | 150 | 2 | 0.1 | 0.1 |

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

`script/loadsim.py` provides the core data-loading utilities:

| Function | Description |
|---|---|
| `load_sim(model)` | Initialise a simulation object and discover available snapshots |
| `load_data(s, num)` | Load a single snapshot (projection maps + star-particle catalogue) |
| `prj_to_xarray(s, expand_domain=False)` | Convert projection maps to a labelled `xarray.Dataset` |
| `get_cutout(data, sp, dx=64)` | Extract a square cutout (±`dx` pc) centred on a star particle |

Each script has a corresponding test. Run tests with:

```bash
pytest script/
```

## Example Notebooks

| Notebook | Description |
|---|---|
| `notebook/example1_read_plot_prj.ipynb` | Load a snapshot; plot EM and Σ_gas maps with star-particle overlays; inspect SFR history and supernova log |
| `notebook/example2_xarray_shear_periodic_cutouts.ipynb` | Convert projections to xarray; tile with shear-periodic BCs; extract per-cluster cutout time-series |

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for a log of major changes.
