"""Reproduce local decisions and check preserved native observations offline."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from audits.native_lfsr_v1.check import run, step

HERE = Path(__file__).resolve().parent


def main():
    for name, expected in json.loads((HERE / 'MANIFEST.json').read_text())['sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise SystemExit('Hash mismatch: ' + name)
    result, _ = run()
    expected = json.loads((HERE / 'expected.json').read_text())
    if result != expected:
        raise SystemExit('Local certificate workload changed')
    native = json.loads((HERE / 'native/RESULTS.json').read_text())
    wanted = {
        'shr3': (0, 'maximal'), 'xorrot32_default': (0, 'maximal'),
        'xoroshiro128pp': (0, 'maximal'), 'xoshiro256pp': (0, 'maximal'),
        'xorrot32_bad1': (1, 'not_maximal'), 'xorrot32_bad2': (1, 'not_maximal'),
        'splitmix': (2, 'not_lfsr'), 'sfc64': (2, 'not_lfsr'),
    }
    if len(native['cases']) != 8 or {r['name'] for r in native['cases']} != set(wanted):
        raise SystemExit('Native corpus mismatch')
    for row in native['cases']:
        # Upstream statuses are checked together with the retained raw logs.
        if row['timed_out'] or row['returncode'] != wanted[row['name']][0]:
            raise SystemExit('Native status mismatch: ' + row['name'])
        for kind in ('stdout', 'stderr'):
            raw = (HERE / 'native' / row[kind + '_file']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != row[kind + '_sha256']:
                raise SystemExit('Native log mismatch: ' + row['name'])
        stdout = (HERE / 'native' / row['stdout_file']).read_text()
        phrase = {0: 'The LFSR has a maximal period',
                  1: 'The LFSR period is not maximal',
                  2: 'The verification cannot be applied to this PNG'}[row['returncode']]
        if phrase not in stdout:
            raise SystemExit('Native textual verdict mismatch: ' + row['name'])
    probes = json.loads((HERE / 'native/TRANSITION_PROBES.json').read_text())
    if len(probes['rows']) != 160:
        raise SystemExit('Native transition sample count changed')
    for row in probes['rows']:
        name = 'xorrot32' if row['name'] == 'xorrot32_default' else row['name']
        if step(name, row['input']) != row['output']:
            raise SystemExit('Native C/source translation mismatch: ' + name)
    print('PASS: four matched certificate controls, eight native records, 160 C transitions.')
    print('Offline replay validates retained evidence; it does not rerun the native binaries.')


if __name__ == '__main__':
    main()
