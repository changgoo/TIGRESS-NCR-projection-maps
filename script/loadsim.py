"""
loadsim.py — Utilities for loading TIGRESS-NCR simulation data.

Functions
---------
load_sim      : Initialize a pyathena LoadSim object for a named model.
load_data     : Load a single snapshot (projection maps + star particles).
prj_to_xarray : Convert the loaded projection dict to an xarray Dataset.
get_cutout    : Extract a small spatial cutout centred on a star particle.
"""

import sys
import os
import glob

import pyathena as pa
from pyathena.util.expand_domain import expand_xy

import pandas as pd
import xarray as xr
import numpy as np


# Directory that contains this script; used to resolve relative data paths.
basedir = os.path.dirname(__file__)


def load_sim(model):
    """Initialize a simulation object for the given paper model name.

    Parameters
    ----------
    model : str
        Short paper model name (e.g. ``'R8-b1-Z1.0'``).  Must match one of
        the 28 models listed in Table 2 of arXiv:2405.19227 and correspond to
        a directory under ``data/``.

    Returns
    -------
    s : pa.LoadSim
        Simulation object with additional attributes:
        ``s.files['prj']`` — sorted list of projection pickle paths,
        ``s.nums``         — list of available snapshot numbers,
        ``s.hst``          — history DataFrame (read on first call),
        ``s.sn``           — supernova log DataFrame (read on first call).
    """
    data_dir = os.path.join(basedir, "../data/", model)
    s = pa.LoadSim(data_dir, verbose=True)

    # Discover projection pickle files and extract their snapshot numbers.
    s.files["prj"] = sorted(glob.glob(os.path.join(data_dir, "prj", "*.p")))
    s.nums = [int(os.path.basename(f[f.rfind("_")+1:f.rfind(".")])) for f in s.files["prj"]]

    # Read time-series history files if not already loaded.
    if not hasattr(s, "hst"):
        s.hst = pa.read_hst(s.files["hst"])

    if not hasattr(s, "sn"):
        s.sn = pa.read_hst(s.files["sn"])

    return s


def load_data(s, num):
    """Load a single snapshot into the simulation object.

    Populates ``s.prj``, ``s.sp``, ``s.sp_src``, and ``s.time`` in-place.

    Parameters
    ----------
    s : pa.LoadSim
        Simulation object returned by :func:`load_sim`.
    num : int
        Snapshot number to load.  Must be present in ``s.nums``.

    Notes
    -----
    ``s.sp_src`` contains only active (non-zero mass) star particles younger
    than 20 Myr, which are the radiation/CR source particles in TIGRESS-NCR.
    """
    if num not in s.nums:
        raise ValueError(
            f"Snapshot {num} is not available. "
            f"Valid range: {s.nums[0]}–{s.nums[-1]}."
        )
    data_dir = s.basedir
    # Projection maps stored as pickled dicts: keys are field names,
    # values are 2-D arrays on the (x, y) plane.
    s.prj = pd.read_pickle(os.path.join(data_dir, "prj", f"prj_{num:04d}.p"))
    # Star-particle VTK file contains position, mass, age, etc.
    s.sp = pa.read_starpar_vtk(
        os.path.join(data_dir, "starpar", f"{s.problem_id}.{num:04d}.starpar.vtk")
    )
    # Restrict to active source particles: mass > 0 and age < 20 Myr.
    s.sp_src = s.sp.where((s.sp.mage < 20) & (s.sp.mass > 0)).dropna()
    s.time = s.sp.time


def prj_to_xarray(s, expand_domain=False):
    """Convert the projection dict in ``s.prj`` to a labelled xarray Dataset.

    The simulation uses a uniform Cartesian grid so cell coordinates are
    reconstructed directly from the domain metadata stored in ``s.domain``.

    Parameters
    ----------
    s : pa.LoadSim
        Simulation object with ``s.prj`` and ``s.domain`` populated.
    expand_domain : bool, optional
        If ``True``, apply shear-periodic boundary tiling via
        ``pyathena.util.expand_domain.expand_xy`` and crop the result to a
        2× domain (one extra copy on each side).  Useful for extracting
        cutouts near the domain boundary without edge artefacts.

    Returns
    -------
    ds : xr.Dataset
        Dataset with coordinates ``x``, ``y`` (pc) and ``time`` (code units).
        Fields are whatever was saved in ``s.prj['z']`` (e.g. ``Sigma_gas``,
        ``Sigma_H2``, ``Sigma_HI``, ``EM``).
    """
    # Build cell-face coordinates from domain metadata, then derive cell centres.
    xfc = [np.linspace(s.domain["le"][i], s.domain["re"][i], s.domain["Nx"][i]+1)
           for i in range(3)]
    xcc = [0.5*(fc_[1:]+fc_[:-1]) for fc_ in xfc]

    prj = s.prj

    # Pack each 2-D field into a labelled DataArray (y, x order matches array layout).
    ds = xr.Dataset()
    for f in list(prj["z"].keys()):
        ds[f] = xr.DataArray(prj["z"][f], coords=[xcc[1], xcc[0]], dims=["y", "x"])

    if expand_domain:
        # Tile the domain using shear-periodic boundary conditions.
        ds_exp = expand_xy(s, ds, time=s.time)
        # Crop to 2× domain — one extra copy per side is sufficient for cutouts.
        xmin = s.domain["le"][0] - s.domain["Lx"][0]*0.5
        xmax = s.domain["re"][0] + s.domain["Lx"][0]*0.5
        ymin = s.domain["le"][1] - s.domain["Lx"][1]*0.5
        ymax = s.domain["re"][1] + s.domain["Lx"][1]*0.5
        ds = ds_exp.sel(x=slice(xmin, xmax), y=slice(ymin, ymax))

    return ds.assign_coords(time=s.time)


def get_cutout(data, sp, dx=64):
    """Extract a square spatial cutout centred on a star particle.

    Coordinates in the returned Dataset are re-centred so that (x=0, y=0)
    corresponds to the nearest grid cell to the particle, making cutouts from
    different snapshots or particles directly comparable.  The absolute
    position and particle metadata are stored as scalar coordinates.

    Parameters
    ----------
    data : xr.Dataset
        Full (or expanded) projection Dataset with ``x`` and ``y`` coords in pc.
    sp : pd.Series
        A single row from a star-particle DataFrame, with at least
        ``x1`` (x-position), ``x2`` (y-position), ``mage`` (mean age, Myr),
        and ``mass`` (M_sun) columns.
    dx : float, optional
        Half-width of the cutout in pc (default 64 pc → 128 pc box).

    Returns
    -------
    cutout : xr.Dataset
        Subset of ``data`` within ±dx pc of the particle, with additional
        scalar coordinates: ``x0``, ``y0`` (grid-snapped centre in pc),
        ``xp``, ``yp`` (exact particle position in pc), ``mage``, ``mass``.
    """
    # Snap the particle position to the nearest grid cell.
    center = data.sel(x=sp["x1"], y=sp["x2"], method="nearest")
    cutout = data.sel(x=slice(center.x-dx, center.x+dx),
                      y=slice(center.y-dx, center.y+dx))

    # Shift x/y to particle-centred frame and attach metadata as coordinates.
    cutout = cutout.assign_coords(
        x=cutout.x.data - center.x.data,
        y=cutout.y.data - center.y.data,
        x0=center.x.data,   # grid-snapped absolute x (pc)
        y0=center.y.data,   # grid-snapped absolute y (pc)
        xp=sp["x1"],        # exact particle x (pc)
        yp=sp["x2"],        # exact particle y (pc)
        mage=sp["mage"],    # mass-weighted mean age of particle (Myr)
        mass=sp["mass"],    # particle mass (M_sun)
    )
    return cutout