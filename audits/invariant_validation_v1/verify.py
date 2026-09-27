"""Standard-library generator/semantics replay; native solver run is optional."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    for name,sha in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:
            raise SystemExit('Changed gate input: '+name)
    with tempfile.TemporaryDirectory(prefix='alc-invariant-gate-') as td:
        out=Path(td)/'fresh.json'
        cmd=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(cmd+[str(HERE/'gate.py'),'--output',str(out)],cwd=ROOT,check=True,timeout=30,
                       stdout=subprocess.DEVNULL)
        expected=json.loads((HERE/'expected.json').read_text())
        if hashlib.sha256(out.read_bytes()).hexdigest()!=expected['complete_report_sha256']:
            raise SystemExit('Gate controls changed; original evidence was not overwritten.')
    print('PASS: 20 frozen invariant controls; 1,700 predicate/step checks; 332 DAG nodes.')
    print('Native cvc5 observations are separate evidence, not implied by this local replay.')

if __name__=='__main__':main()
