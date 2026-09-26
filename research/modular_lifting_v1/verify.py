"""Reproduce the complete modular-layer check without changing stored evidence."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    for path,sha in manifest['sha256'].items():
        f=ROOT/path
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=sha:
            raise SystemExit('Missing or changed modular research input: '+path)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-modular-lifting-') as temp:
        fresh=Path(temp)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(fresh)],cwd=ROOT,
                       stdout=subprocess.DEVNULL,check=True,timeout=900,
                       env={**os.environ,'PYTHONHASHSEED':'0'})
        if fresh.read_bytes()!=gzip.decompress((HERE/'expected.json.gz').read_bytes()):
            raise SystemExit('Exact modular result differs; old evidence remains untouched')
    print('PASS: 67,180 small modular cases, 117,170 derived field proofs, and a separate 64-bit example.')
    print('Polynomial certificate composition is not a publication-novelty or native-solver performance certificate.')


if __name__=='__main__':main()
