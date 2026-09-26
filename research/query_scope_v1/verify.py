"""Verify the additive query-scope audit, never overwrite prior evidence."""
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
    for name,expected in manifest['sha256'].items():
        path=ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise SystemExit('Missing or changed query-scope input: '+name)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-query-scope-') as temp:
        path=Path(temp)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(path)],cwd=ROOT,
                       check=True,stdout=subprocess.DEVNULL,timeout=240,
                       env={**os.environ,'PYTHONHASHSEED':'0'})
        if path.read_bytes()!=gzip.decompress((HERE/'expected.json.gz').read_bytes()):
            raise SystemExit('Exact query-scope report differs; prior evidence is unchanged.')
    print('PASS: 755 formula reductions, 13,498 common-exponent queries, and 5,280 closed-observation queries.')
    print('Hardness is established by reductions, not finite tests. No new production schema or novelty clearance.')


if __name__=='__main__':
    main()
