"""Verify direct positive ring certificates and optionally repeat the comparison."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sympy',action='store_true');args=p.parse_args()
    for path,sha in json.loads((HERE/'MANIFEST.json').read_text())['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:
            raise SystemExit('Changed direct-proof input: '+path)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-direct-modular-') as td:
        report=Path(td)/'results.json';bench=Path(td)/'timing.json'
        command=prefix+[str(HERE/'check.py'),'--output',str(report)]
        if args.sympy:command+=['--benchmark',str(bench),'--repeats','1']
        subprocess.run(command,cwd=ROOT,check=True,stdout=subprocess.DEVNULL,timeout=300)
        if report.read_bytes()!=(HERE/'expected.json').read_bytes():raise SystemExit('Exact direct-proof audit differs')
        if args.sympy:
            actual=json.loads(bench.read_text());expected=json.loads((HERE/'timing_observations.json').read_text())
            keys=['width','problem','first','period','direct_certificate','direct_bytes','layered_bytes','layered_sha256']
            clean=lambda x:[{k:r[k] for k in keys} for r in x['cases']]
            if clean(actual)!=clean(expected):raise SystemExit('Matched proof outputs differ')
    print('PASS: direct positive ring certificates, false-claim controls, and dependency manifest.')
    print('The smaller witness is a use of established order certification, not a new orbit algorithm.')


if __name__=='__main__':main()
