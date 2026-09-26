"""Check committed integrity and reproduce the exact finite audit, without edits."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent


def main():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    for path, expected in manifest['sha256'].items():
        actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit('Hash mismatch: '+path)
    # Launch tests in a new interpreter so process-global caches cannot replace checks.
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)
    with tempfile.TemporaryDirectory(prefix='alc-verification-') as temp:
        output=Path(temp)/'exhaustive.json'
        with output.open('w',encoding='utf-8') as stream:
            subprocess.run([sys.executable,'-m','tests.exhaustive'],cwd=ROOT,check=True,stdout=stream)
        if output.read_bytes() != (ROOT/'evidence/exhaustive.json').read_bytes():
            raise SystemExit('Regenerated finite audit differs; stored evidence was not changed')
    print('PASS: source hashes, regression tests, and exact 4,772-case finite audit.')
    print('This is a positive-certificate prototype, not an advantage or novelty certificate.')


if __name__=='__main__':main()
