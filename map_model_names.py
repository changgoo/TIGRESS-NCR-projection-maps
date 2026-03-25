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


def main():
    basedir = sys.argv[1] if len(sys.argv) > 1 else BASEDIR

    folders = sorted(
        d for d in os.listdir(basedir)
        if os.path.isdir(os.path.join(basedir, d))
    )

    rows = []
    for folder in folders:
        params = parse_params(folder)
        model_name, err = get_model_name(folder, params)
        rows.append(dict(
            basename=folder,
            model_name=model_name if model_name else f'[{err}]',
            beta=params.get('beta', ''),
            Z_gas=params.get('Z_gas', ''),
            Z_dust=params.get('Z_dust', ''),
            ok=err is None,
        ))

    # ── write markdown table ──────────────────────────────────────────────────
    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'model_name_mapping.md')
    n_ok  = sum(r['ok'] for r in rows)
    n_err = len(rows) - n_ok

    with open(outfile, 'w') as f:
        f.write('# Model Name Mapping\n\n')
        f.write(f'Total: {len(rows)} folders &nbsp;|&nbsp; mapped: {n_ok} &nbsp;|&nbsp; errors: {n_err}\n\n')
        f.write('| basename | model_name | beta | Z_gas | Z_dust |\n')
        f.write('|----------|------------|-----:|------:|-------:|\n')
        for r in rows:
            flag = '' if r['ok'] else ' ⚠️'
            f.write(
                f"| `{r['basename']}` | {r['model_name']}{flag} "
                f"| {r['beta']} | {r['Z_gas']} | {r['Z_dust']} |\n"
            )

    print(f"Written to {outfile}")
    print(f"Total: {len(rows)} folders  |  mapped: {n_ok}  |  errors: {n_err}")
    if n_err:
        print("\nCould not map:")
        for r in rows:
            if not r['ok']:
                print(f"  {r['basename']:60s}  {r['model_name']}")


if __name__ == '__main__':
    main()
