"""Optional native scalar comparison; no fixture or timing overwrite."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    for path,sha in json.loads((HERE/'MANIFEST.json').read_text())['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:
            raise SystemExit('Missing or changed comparison input: '+path)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-native-scalar-') as td:
        result=Path(td)/'exact.json';timings=Path(td)/'timing.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(result),
                       '--timings',str(timings),'--repeats','1'],cwd=ROOT,
                       stdout=subprocess.DEVNULL,check=True,timeout=300)
        actual=json.loads(result.read_text());expected=json.loads((HERE/'expected.json').read_text())
        current=actual.pop('sympy_version');expected.pop('sympy_version')
        if actual!=expected:
            raise SystemExit('Native comparison changed; original evidence was not overwritten.')
    print('PASS: 13,602 native scalar decisions; 1,122 paired certificate cases; six matched examples.')
    print('SymPy '+current+'. The recorded native solution is faster on these scalar controls; no speedup is certified.')


if __name__=='__main__':main()
