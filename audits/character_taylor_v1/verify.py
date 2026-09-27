"""Replay the exact full field-source comparison; no fixture or network writes."""
from pathlib import Path
import gzip,hashlib,json,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    for name,expected in json.loads((HERE/'MANIFEST.json').read_text())['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise SystemExit('Changed or missing comparison dependency: '+name)
    prefix=[sys.executable]+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='alc-character-taylor-') as d:
        out=Path(d)/'fresh.json'
        subprocess.run(prefix+[str(HERE/'check.py'),'--output',str(out)],cwd=ROOT,
                       check=True,timeout=240,stdout=subprocess.DEVNULL,
                       env={**os.environ,'PYTHONHASHSEED':'0'})
        if out.read_bytes()!=gzip.decompress((HERE/'expected.json.gz').read_bytes()):
            raise SystemExit('Exact report differs; no evidence was overwritten.')
    print('PASS: 661 source certificates; 7,209 matched target queries; 240 larger closed-form controls.')
    print('Original compiler, cyclic solver and unipotent decoder are not called by the alternative path.')
    print('Shared elementary arithmetic/primality; no first-hit, timing, formal-proof or novelty claim.')

if __name__=='__main__':main()
