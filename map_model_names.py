#!/usr/bin/env python3
"""
map_model_names.py — Map simulation folder basenames to paper model names.

Replicates the logic of LowZData.get_model_name() by parsing beta, Z_gas,
and Z_dust directly from the folder basename using regex, without loading
any simulation data.

Usage:
    python map_model_names.py [basedir]

Output:
    model_name_mapping.txt  (written next to this script)
"""

import os
import re
import sys

BASEDIR = "/tigerdata/EOSTRIKE/TIGRESS-NCR/"


def parse_params(basename):
    """Parse physical parameters from folder basename.

    Returns a dict with any of: 'beta' (int), 'Z_gas' (float), 'Z_dust' (float).
    Missing keys mean the value could not be determined from the name.
    """
    params = {}

    # beta: .b{N}. e.g. .b1. .b10. .b2.
    m = re.search(r'\.b(\d+)\.', basename)
    if m:
        params['beta'] = int(m.group(1))

    # Z_gas: .Zg{N} e.g. .Zg0.1 .Zg1 .Zg0.01 .Zg3
    m = re.search(r'\.Zg(\d+(?:\.\d+)?)', basename)
    if m:
        params['Z_gas'] = float(m.group(1))

    # Z_dust: .Zd{N} e.g. .Zd0.025 .Zd1 .Zd0.1
    m = re.search(r'\.Zd(\d+(?:\.\d+)?)', basename)
    if m:
        params['Z_dust'] = float(m.group(1))

    return params


def get_sigma0(basename):
    """Return the initial gas surface density Sigma_0 [Msun/pc^2].

    Explicit SXX tags take precedence; otherwise default by galaxy model:
      R8   → 12,  LGR4 → 50  (LGR2/LGR8 always carry an explicit tag)
    """
    m = re.search(r'_S(\d+)', basename)
    if m:
        return int(m.group(1))
    if basename.startswith('R8'):
        return 12
    if basename.startswith('LGR4'):
        return 50
    return None


def get_model_name(basename, params):
    """Replicate LowZData.get_model_name() from parsed params.

    Returns (model_name, error_message).  On success, error_message is None.
    """
    beta  = params.get('beta')
    Z_gas = params.get('Z_gas')
    Z_dust = params.get('Z_dust')

    # ── head ──────────────────────────────────────────────────────────────────
    if 'S30' in basename:
        head = 'S30'
    elif 'S150' in basename:
        head = 'S150'
        if 'Om01' in basename:
            head += '-Om100q0'
        elif 'Om02' in basename:
            head += '-Om200'
    elif 'S100' in basename:
        head = 'S100'
    elif 'S05' in basename:
        head = 'S05'
    else:
        # Standard runs: prefix from first underscore-delimited token + beta
        head = basename.split('_')[0]
        if beta is None:
            return None, 'missing beta'
        head += f'-b{int(beta)}'

    # ── ztail ─────────────────────────────────────────────────────────────────
    if Z_gas is None or Z_dust is None:
        return None, 'missing Z_gas or Z_dust'

    if Z_gas == Z_dust:
        ztail = f'Z{Z_gas:3.1f}'
    else:
        ztail = f'Zg{Z_gas:3.1f}Zd{Z_dust:5.3f}'

    if 'rstZ01' in basename:
        ztail += 'r'

    return f'{head}-{ztail}', None


# Folders explicitly excluded from the paper model list
SKIP = {
    'LGR4_4pc_NCR.full.b10.v3.iCR4.Zg0.1.Zd0.025',   # no xy counterpart
    'LGR4_4pc_NCR.full.b10.v3.iCR4.Zg0.3.Zd0.3',      # no xy counterpart
    'R8_8pc_NCR.full.b1.v3.iCR4.Zg0.1.Zd0.1.SBZ002_V00',  # variant run
}


def find_early_runs(folders):
    """Return the set of folder names that are 'early' runs.

    A folder is early if its name equals the prefix-before-.xy of some
    other folder that contains 'xy', mirroring the _get_models logic.
    The iCR4/iCR5 substitution is also checked (some early runs use iCR4
    while the final run uses iCR5).
    """
    early = set()
    for f in folders:
        if 'xy' not in f:
            continue
        mearly = f[:f.rfind('xy') - 1]
        for f2 in folders:
            if f2 == mearly or f2 == mearly.replace('iCR5', 'iCR4'):
                early.add(f2)
    return early


def main():
    basedir = sys.argv[1] if len(sys.argv) > 1 else BASEDIR

    folders = sorted(
        d for d in os.listdir(basedir)
        if os.path.isdir(os.path.join(basedir, d))
    )

    early_runs = find_early_runs(folders)

    rows = []
    for folder in folders:
        params = parse_params(folder)
        model_name, err = get_model_name(folder, params)

        # Keep only paper models:
        if err is not None:
            continue                              # missing beta or Z info
        if params.get('Z_gas') == 0.01 or params.get('Z_dust') == 0.01:
            continue                              # Z=0.01 not in paper
        if folder in early_runs:
            continue                              # early evolution run
        if folder in SKIP:
            continue                              # manually excluded

        rows.append(dict(
            basename=folder,
            model_name=model_name,
            sigma0=get_sigma0(folder),
            beta=params.get('beta', ''),
            Z_gas=params.get('Z_gas', ''),
            Z_dust=params.get('Z_dust', ''),
        ))

    # Sort: ascending Sigma_0, then descending Z_gas
    rows.sort(key=lambda r: (r['sigma0'], -r['Z_gas']))

    # ── write markdown table ──────────────────────────────────────────────────
    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'model_name_mapping.md')
    with open(outfile, 'w') as f:
        f.write('# Model Name Mapping\n\n')
        f.write(f'{len(rows)} paper models (excludes missing-parameter folders and Z=0.01 runs)\n\n')
        f.write('| basename | model_name | Sigma0 | beta | Z_gas | Z_dust |\n')
        f.write('|----------|------------|-------:|-----:|------:|-------:|\n')
        for r in rows:
            f.write(
                f"| `{r['basename']}` | {r['model_name']} "
                f"| {r['sigma0']} | {r['beta']} | {r['Z_gas']} | {r['Z_dust']} |\n"
            )

    print(f"Written to {outfile}")
    print(f"{len(rows)} paper models")


if __name__ == '__main__':
    main()
