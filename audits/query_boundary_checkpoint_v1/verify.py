"""Replay the authentic pending audit in isolation, preserving live research code.

The compact archive contains only its eleven original additive files. Each
member and each currently supplied dependency is hash-checked before execution.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,subprocess,sys,tempfile,zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sympy',action='store_true');args=parser.parse_args()
    ledger=json.loads((HERE/'MANIFEST.json').read_text())
    for name,sha in ledger['wrapper_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=sha:raise SystemExit('Wrapper changed: '+name)
    archive=HERE/'additions.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=ledger['archive_sha256']:raise SystemExit('Archive changed.')
    with tempfile.TemporaryDirectory(prefix='alc-preserved-boundary-') as td:
        root=Path(td)
        with zipfile.ZipFile(archive) as z:
            if set(z.namelist())!=set(ledger['member_sha256']) or len(z.namelist())!=len(ledger['member_sha256']):
                raise SystemExit('Archive membership differs.')
            for name,sha in ledger['member_sha256'].items():
                p=PurePosixPath(name)
                if p.is_absolute() or '..' in p.parts:raise SystemExit('Unsafe member.')
                info=z.getinfo(name)
                if info.file_size>1_000_000:raise SystemExit('Oversized member.')
                data=z.read(name)
                if hashlib.sha256(data).hexdigest()!=sha:raise SystemExit('Member changed: '+name)
                out=root/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        original=json.loads((root/'research/query_boundary_audit_v1/MANIFEST.json').read_text())
        for name,sha in original['sha256'].items():
            destination=root/name
            if not destination.exists():
                data=(ROOT/name).read_bytes()
                if hashlib.sha256(data).hexdigest()!=sha:raise SystemExit('Original dependency changed: '+name)
                destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
        cmd=[sys.executable]+(['-O'] if not __debug__ else [])
        cmd+=[str(root/'research/query_boundary_audit_v1/verify.py')]
        if args.sympy:cmd+=['--sympy']
        subprocess.run(cmd,cwd=root,check=True,timeout=240,env={**os.environ,'PYTHONHASHSEED':'0'})
    print('PASS: eleven authentic pending additions replayed without replacing the live query-scope audit.')


if __name__=='__main__':main()
