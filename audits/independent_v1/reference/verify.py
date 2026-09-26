"""Offline integrity, documentation, and reproducibility checks; no fixture writes."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def main():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    for name, digest in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise SystemExit('Hash mismatch: '+name)
    required = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
                if p.is_file() and not any(x in p.parts for x in ('.git','__pycache__','dist','build','.venv'))
                and not any(x.endswith('.egg-info') for x in p.parts)
                and p.name not in ('MANIFEST.json',) and not p.suffix in ('.pyc','.pyo')}
    # Exact source checkout coverage; generated local extras must not hide from review.
    if required != set(manifest['sha256']):
        raise SystemExit('Manifest coverage differs: '+str(sorted(required ^ set(manifest['sha256']))))
    if git_blob((ROOT/'LICENSE').read_bytes()) != 'e17a781bf47c4aadf18b68fc593846a1193b86c1':
        raise SystemExit('Original license changed.')
    if git_blob((ROOT/'history/ALGEBRAIC_ORBIT_INDEXING_17.md').read_bytes()) != '18a2bd4b39077a6b4a32e8b299b133796e6bf6fb':
        raise SystemExit('Historical note changed.')
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            target = target.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            if not (path.parent/target).exists():
                raise SystemExit(f'Broken local link in {path.relative_to(ROOT)}: {target}')
    with tempfile.TemporaryDirectory(prefix='alc-reproduce-') as td:
        source = Path(td)/'source'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git','__pycache__','*.egg-info','dist','build','.venv'))
        output = Path(td)/'new-results.json'
        env = dict(os.environ, PYTHONHASHSEED='0')
        cmd = [sys.executable] + (['-O'] if not __debug__ else [])
        subprocess.run(cmd+[str(source/'tests/audit.py'), '--output', str(output)],
                       check=True, timeout=120, stdout=subprocess.DEVNULL, cwd=source, env=env)
        if output.read_bytes() != (ROOT/'reports/expected.json').read_bytes():
            raise SystemExit('Deterministic report mismatch; no stored evidence was overwritten.')
    print('PASS: manifest, original license, historical note, local links, and exact certificate/consumer audit.')
    print('4,834 state-target cases; 6,084 schedule intersections; malformed-input and resource-limit controls.')
    print('Original local scout ZIP not recovered or rerun. No novelty, formal verification, or speedup claim.')


if __name__ == '__main__':
    main()
