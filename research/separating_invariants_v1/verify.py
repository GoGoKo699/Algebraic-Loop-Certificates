"""Pin dependencies and reproduce the invariant audit without changing fixtures."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    for name,expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise SystemExit('Missing or changed invariant input: '+name)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-separating-check-') as td:
        path=Path(td)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(path)],cwd=ROOT,
                       stdout=subprocess.DEVNULL,check=True,timeout=180)
        if path.read_bytes()!=(HERE/'expected.json').read_bytes():
            raise SystemExit('Invariant audit differs; no old evidence was overwritten.')
    print('PASS: 5,189 decisions; 2,876 separating certificates; 706 full-state inductive predicates.')
    print('Target-independent reuse and false-proof controls pass. No priority or runtime advantage certified.')

if __name__=='__main__':main()
