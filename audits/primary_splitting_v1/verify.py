"""Replay the matched reduction-layer audit without changing old evidence."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    ledger=json.loads((HERE/'MANIFEST.json').read_text())
    for path,expected in ledger['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:
            raise SystemExit('Missing or changed comparison dependency: '+path)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-primary-splitting-') as td:
        report=Path(td)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(report)],cwd=ROOT,
                       check=True,stdout=subprocess.DEVNULL,timeout=240,
                       env={**os.environ,'PYTHONHASHSEED':'0'})
        if report.read_bytes()!=(HERE/'expected.json').read_bytes():
            raise SystemExit('Exact comparison differs; no fixture was overwritten.')
    print('PASS: 1,408 sources; 25,068 target comparisons; 40,060 abstract group pairs.')
    print('Shared compiler and p-group kernel; only the lifting reduction is independently compared.')
    print('No new API, full native baseline, runtime advantage, or publication novelty claimed.')

if __name__=='__main__':main()
