"""Tests for map_model_names.py."""

import pytest
from map_model_names import parse_params, get_model_name, lookup, EXTRA_MODELS


# ── parse_params ──────────────────────────────────────────────────────────────

def test_parse_params_standard():
    params = parse_params('R8_8pc_NCR.full.xy256.b1.v3.iCR5.Zg1.0.Zd1.0')
    assert params['beta'] == 1
    assert params['Z_gas'] == pytest.approx(1.0)
    assert params['Z_dust'] == pytest.approx(1.0)


def test_parse_params_decoupled_Z():
    params = parse_params('R8_8pc_NCR.full.xy256.b1.v3.iCR5.Zg0.1.Zd0.025')
    assert params['Z_gas'] == pytest.approx(0.1)
    assert params['Z_dust'] == pytest.approx(0.025)


def test_parse_params_high_res_r8():
    """High-res R8-4pc model has no beta/Z tags."""
    params = parse_params('R8_4pc_NCR.full.xy2048.eps0.np768.has')
    assert 'beta' not in params
    assert 'Z_gas' not in params
    assert 'Z_dust' not in params


def test_parse_params_high_res_lgr4():
    """High-res LGR4-2pc model has no beta/Z tags."""
    params = parse_params('LGR4_2pc_NCR.full.xy1024.eps1.e-8.np768')
    assert 'beta' not in params
    assert 'Z_gas' not in params
    assert 'Z_dust' not in params


# ── get_model_name ────────────────────────────────────────────────────────────

def test_get_model_name_r8_z1():
    params = {'beta': 1, 'Z_gas': 1.0, 'Z_dust': 1.0}
    name, err = get_model_name('R8_8pc_NCR.full.xy256.b1.v3.iCR5.Zg1.0.Zd1.0', params)
    assert err is None
    assert name == 'R8-b1-Z1.0'


def test_get_model_name_decoupled():
    params = {'beta': 1, 'Z_gas': 0.1, 'Z_dust': 0.025}
    name, err = get_model_name('R8_8pc_NCR.full.xy256.b1.v3.iCR5.Zg0.1.Zd0.025', params)
    assert err is None
    assert name == 'R8-b1-Zg0.1Zd0.025'


def test_get_model_name_missing_beta():
    params = {'Z_gas': 1.0, 'Z_dust': 1.0}
    name, err = get_model_name('R8_4pc_NCR.full.xy2048.eps0.np768.has', params)
    assert name is None
    assert err == 'missing beta'


# ── EXTRA_MODELS ──────────────────────────────────────────────────────────────

def test_extra_models_keys():
    assert 'R8_4pc_NCR.full.xy2048.eps0.np768.has' in EXTRA_MODELS
    assert 'LGR4_2pc_NCR.full.xy1024.eps1.e-8.np768' in EXTRA_MODELS


def test_extra_models_values():
    assert EXTRA_MODELS['R8_4pc_NCR.full.xy2048.eps0.np768.has'] == 'R8-4pc'
    assert EXTRA_MODELS['LGR4_2pc_NCR.full.xy1024.eps1.e-8.np768'] == 'LGR4-2pc'


# ── lookup (EXTRA_MODELS path, no basedir access needed) ─────────────────────

def test_lookup_r8_4pc():
    assert lookup('R8_4pc_NCR.full.xy2048.eps0.np768.has') == 'R8-4pc'


def test_lookup_lgr4_2pc():
    assert lookup('LGR4_2pc_NCR.full.xy1024.eps1.e-8.np768') == 'LGR4-2pc'


def test_lookup_unknown_returns_none(tmp_path):
    """An unrecognised basename should return None (basedir is an empty tmp dir)."""
    assert lookup('totally_unknown_run', basedir=str(tmp_path)) is None
