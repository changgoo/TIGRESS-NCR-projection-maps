# TIGRESS-NCR Projection Maps

A curated copy of processed results from TIGRESS-NCR simulations, together with scripts to read and analyze the data.

## Repository Structure

```
.
├── data/                   # Simulation data (not in repo — download separately)
│   └── <model>/
│       ├── prj/            # Projection maps (pickle files)
│       ├── starpar/        # Star particle VTK outputs
│       ├── hst/            # History (time series) outputs
│       └── README.md       # Data summary (file count, size, run metadata)
├── DATA_SUMMARY.md         # File count and size summary across all models
├── notebook/               # Example Jupyter notebooks
├── script/                 # Python analysis scripts
├── test/                   # Tests and data-management utilities
└── DEVELOPMENT.md          # Development log (latest to first)
```

## Data

The `data/` directory is **not included in this repository**. To use the scripts and notebooks, download the data and place it under `data/<model>/` where `<model>` is the short model name (e.g. `R8-b1-Z1.0`).

### Downloading

**Example model (`R8-b1-Z1.0`)** — used in the example notebooks — is available at:

```
https://tigress-web.princeton.edu/~changgoo/TIGRESS-NCR-projection-maps/
```

Download the `R8-b1-Z1.0/` directory and place it at `data/R8-b1-Z1.0/`.

**Full dataset** — all 30 models will be released via Globus (coming soon).

A file count and size summary across all locally available models is in [`DATA_SUMMARY.md`](DATA_SUMMARY.md).

### Models

The 28 models below are from [Kim, Ostriker, et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...972...67K/abstract) (Table 2). Two additional high-resolution models (`R8-4pc`, `LGR4-2pc`) are from [Kim et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...946....3K/abstract). `Sigma0` is the initial gas surface density [M☉/pc²]; `beta` is the initial plasma beta; `Z_gas` and `Z_dust` are gas- and dust-phase metallicities relative to solar.

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
| R8-4pc (\*) | 12 | 1 | 1.0 | 1.0 |
| LGR4-2pc (\*) | 50 | 1 | 1.0 | 1.0 |

(\*) High-resolution models from [Kim et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...946....3K/abstract).

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
pytest test/
```

## Example Notebooks

| Notebook | Description |
|---|---|
| `notebook/example1_read_plot_prj.ipynb` | Load a snapshot; plot EM and Σ_gas maps with star-particle overlays; inspect SFR history and supernova log |
| `notebook/example2_xarray_shear_periodic_cutouts.ipynb` | Convert projections to xarray; tile with shear-periodic BCs; extract per-cluster cutout time-series |

## Attribution

If you use this data or scripts, please cite the relevant papers:

```bibtex
@ARTICLE{2024ApJ...972...67K,
  author = {{Kim}, Chang-Goo and {Ostriker}, Eve C. and {Kim}, Jeong-Gyu and {Gong}, Munan and {Bryan}, Greg L. and {Fielding}, Drummond B. and {Hassan}, Sultan and {Ho}, Matthew and {Jeffreson}, Sarah M.~R. and {Somerville}, Rachel S. and {Steinwandel}, Ulrich P.},
  title = "{Metallicity Dependence of Pressure-regulated Feedback-modulated Star Formation in the TIGRESS-NCR Simulation Suite}",
  journal = {\apj},
  year = 2024,
  month = sep,
  volume = {972},
  number = {1},
  eid = {67},
  pages = {67},
  doi = {10.3847/1538-4357/ad59ab},
  archivePrefix = {arXiv},
  eprint = {2405.19227},
  adsurl = {https://ui.adsabs.harvard.edu/abs/2024ApJ...972...67K},
}

@ARTICLE{2023ApJ...946....3K,
  author = {{Kim}, Chang-Goo and {Kim}, Jeong-Gyu and {Gong}, Munan and {Ostriker}, Eve C.},
  title = "{Introducing TIGRESS-NCR. I. Coregulation of the Multiphase Interstellar Medium and Star Formation Rates}",
  journal = {\apj},
  year = 2023,
  month = mar,
  volume = {946},
  number = {1},
  eid = {3},
  pages = {3},
  doi = {10.3847/1538-4357/acbd3a},
  archivePrefix = {arXiv},
  eprint = {2211.13293},
  adsurl = {https://ui.adsabs.harvard.edu/abs/2023ApJ...946....3K},
}
```
