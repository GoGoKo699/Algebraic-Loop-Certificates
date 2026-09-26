"""Pinned exact research replay; no overwrite and no network installation."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sympy',action='store_true');args=parser.parse_args()
    ledger=json.loads((HERE/'MANIFEST.json').read_text())
    for name,sha in ledger['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:raise SystemExit('Changed research dependency: '+name)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-prime-power-compile-') as td:
        report=Path(td)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(report)],cwd=ROOT,check=True,
                       timeout=240,stdout=subprocess.DEVNULL,env={**os.environ,'PYTHONHASHSEED':'0'})
        if report.read_bytes()!=gzip.decompress((HERE/'expected.json.gz').read_bytes()):
            raise SystemExit('Exact result differs; no stored evidence changed.')
        if args.sympy:
            native=Path(td)/'native.json'
            subprocess.run(prefix+[str(HERE/'native_check.py'),'--output',str(native)],cwd=ROOT,
                           check=True,stdout=subprocess.DEVNULL,timeout=120)
            got=json.loads(native.read_text());expected=json.loads((HERE/'native_results.json').read_text())
            version=got.pop('sympy_version');expected.pop('sympy_version')
            if got!=expected:raise SystemExit('Native comparison differs.')
            print('PASS: 120 native Smith comparisons and 2,868 scalar predicates (SymPy '+version+').')
    print('PASS: 1,414 source compilations; 25,189 exact targets; 23,201 mixed-module p-group checks.')
    print('One residue certificate per source; no target-log search or first-hit claim. Originality remains unestablished.')


if __name__=='__main__':main()
