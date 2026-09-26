"""Run isolated reference verification and cross-implementation checks."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise SystemExit('Audit input changed: '+relative)
    cmd=[sys.executable]+(['-O'] if not __debug__ else [])
    subprocess.run(cmd+[str(HERE/'reference/verify.py')],cwd=HERE/'reference',check=True,timeout=120)
    with tempfile.TemporaryDirectory(prefix='alc-crosscheck-') as temp:
        report=Path(temp)/'report.json'
        subprocess.run(cmd+[str(HERE/'crosscheck.py'),'--output',str(report)],
                       cwd=ROOT,check=True,timeout=120,stdout=subprocess.DEVNULL)
        if report.read_bytes()!=(HERE/'expected.json').read_bytes():
            raise SystemExit('Cross-implementation result differs; no fixture was overwritten.')
    print('PASS: primary and independent checkers agree on 2,282 valid positive certificates;')
    print('both reject false hit claims for 2,552 unreachable targets in the tested finite domain.')
    print('Primary API remains unchanged and positive-only. Reference negative proofs are experimental.')


if __name__=='__main__':
    main()
