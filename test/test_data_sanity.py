"""
Sanity checks for data/ — verify completeness and readability of copied models.

Run after copying one or more models with copy_data.sh:
    pytest test/test_data_sanity.py -v

Tests are skipped automatically when data/ does not exist (e.g. clean checkout).
"""

import glob
import os
import pickle

import pytest

REPO_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_DIR, "data")


def collect_models():
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    )


MODELS = collect_models()


# ── Global checks ─────────────────────────────────────────────────────────────

def test_data_dir_exists():
    if not os.path.isdir(DATA_DIR):
        pytest.skip("data/ not present")


def test_data_summary_exists():
    assert os.path.isfile(os.path.join(REPO_DIR, "DATA_SUMMARY.md")), \
        "DATA_SUMMARY.md missing — run test/update_data_readme.sh"


def test_at_least_one_model():
    if not os.path.isdir(DATA_DIR):
        pytest.skip("data/ not present")
    assert len(MODELS) > 0, "No model directories found under data/"


# ── Per-model checks ──────────────────────────────────────────────────────────

@pytest.fixture(params=MODELS)
def model(request):
    return request.param


@pytest.fixture
def model_dir(model):
    return os.path.join(DATA_DIR, model)


def test_athinput_exists(model_dir):
    assert os.path.isfile(os.path.join(model_dir, "athinput.runtime")), \
        "athinput.runtime missing"


def test_athinput_nonempty(model_dir):
    path = os.path.join(model_dir, "athinput.runtime")
    assert os.path.isfile(path) and os.path.getsize(path) > 0, \
        "athinput.runtime is empty"


def test_hst_file_present(model_dir):
    files = glob.glob(os.path.join(model_dir, "hst", "*.hst"))
    assert len(files) > 0, "No .hst files found in hst/"


def test_sn_file_present(model_dir):
    files = glob.glob(os.path.join(model_dir, "hst", "*.sn"))
    assert len(files) > 0, "No .sn files found in hst/"


def test_prj_files_present(model_dir):
    files = glob.glob(os.path.join(model_dir, "prj", "*.p"))
    assert len(files) > 0, "No .p files found in prj/"


def test_prj_pickle_readable(model_dir):
    """First prj pickle loads as a dict with expected projection keys."""
    files = sorted(glob.glob(os.path.join(model_dir, "prj", "*.p")))
    if not files:
        pytest.skip("No prj files to check")
    with open(files[0], "rb") as f:
        data = pickle.load(f)
    assert isinstance(data, dict), "prj pickle is not a dict"
    for key in ("extent", "x", "y", "z"):
        assert key in data, f"prj pickle missing key '{key}'"


def test_prj_has_sigma_gas(model_dir):
    """Each projection direction contains Sigma_gas."""
    files = sorted(glob.glob(os.path.join(model_dir, "prj", "*.p")))
    if not files:
        pytest.skip("No prj files to check")
    with open(files[0], "rb") as f:
        data = pickle.load(f)
    for direction in ("x", "y", "z"):
        assert "Sigma_gas" in data.get(direction, {}), \
            f"prj['{direction}'] missing 'Sigma_gas'"


def test_starpar_vtk_present(model_dir):
    starpar_dir = os.path.join(model_dir, "starpar")
    if not os.path.isdir(starpar_dir):
        pytest.skip("starpar/ not present")
    files = glob.glob(os.path.join(starpar_dir, "*.vtk"))
    if not files:
        pytest.skip("No .vtk files in starpar/ (model may only have pre-pickled vtk)")
    assert len(files) > 0
