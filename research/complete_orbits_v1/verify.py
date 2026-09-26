"""Reproduce the research evidence without changing the production interface.

A root checkout (or the supplied explicitly labeled subset) is required. The
optional SymPy check is separate; no network or dependency install is performed.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--sympy',action='store_true',help='Also run the optional native SymPy comparison.')
    args=parser.parse_args(argv)
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    for relative,expected in manifest['sha256'].items():
        path=ROOT/relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise SystemExit('Missing or changed research input: '+relative)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-complete-decision-') as td:
        report=Path(td)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(report)],cwd=ROOT,
                       stdout=subprocess.DEVNULL,check=True,timeout=120,
                       env={**os.environ,'PYTHONHASHSEED':'0'})
        if report.read_bytes()!=gzip.decompress((HERE/'expected.json.gz').read_bytes()):
            raise SystemExit('Exact research report differs; stored evidence was not overwritten.')
        if args.sympy:
            output=Path(td)/'sympy.json'
            subprocess.run(prefix+[str(HERE/'sympy_check.py'),'--output',str(output)],cwd=ROOT,
                           stdout=subprocess.DEVNULL,check=True,timeout=120)
            result=json.loads(output.read_text()); expected=json.loads((HERE/'sympy_results.json').read_text())
            current_version=result.pop('sympy_version'); expected.pop('sympy_version')
            if result!=expected:
                raise SystemExit('Native comparison disagrees; old report was not changed.')
            print('PASS: optional native factor/scalar comparisons (SymPy '+current_version+').')
    print('PASS: pinned research source and primary dependencies; exact 6,205-case decision audit;')
    print('2,374 unchanged-primary positive replays, 403 unipotent-ring and 246 irreducibility controls.')
    print('Research schema only: no production API promotion, formal verification, novelty or speedup certified.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
