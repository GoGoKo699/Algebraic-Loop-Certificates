"""Reproduce source-only exact orbit recognition without overwriting evidence."""
from pathlib import Path
import gzip, hashlib, json, os, subprocess, sys, tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    for name,expected in json.loads((HERE/'MANIFEST.json').read_text())['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise SystemExit('Missing or changed compiled-orbit dependency: '+name)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-compiled-orbit-') as d:
        result=Path(d)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(result)],cwd=ROOT,
                       check=True,stdout=subprocess.DEVNULL,timeout=180,
                       env={**os.environ,'PYTHONHASHSEED':'0'})
        if result.read_bytes()!=gzip.decompress((HERE/'expected.json.gz').read_bytes()):
            raise SystemExit('Exact compilation report differs; old fixtures were not changed.')
    print('PASS: 657 source compilations, 5,354 exhaustive target queries, and 670 additional controls.')
    print('1,728 compatibility graphs and 74,088 residue assignments; query/search boundaries checked.')
    print('No first-hit recovery, general fast synthesis, novelty clearance, or formal code proof asserted.')

if __name__=='__main__':main()
