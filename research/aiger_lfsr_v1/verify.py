"""Deterministic evidence; independent raw gates and finite small-state checks."""

import hashlib
import json
from collections import deque
from pathlib import Path

from .check import Rejected, check
from .source_aware import odd_order

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def raw_model(raw):
    """Independent literal-list evaluator; no symbolic checker routines used."""
    lines = raw.decode("ascii").splitlines()
    _, m, i, l, o, a = lines[0].split()
    m, i, l, o, a = map(int, (m, i, l, o, a))
    ins = [int(x) for x in lines[1:1+i]]
    latch = [tuple(map(int, x.split())) for x in lines[1+i:1+i+l]]
    out = int(lines[1+i+l])
    gates = [tuple(map(int, x.split())) for x in lines[2+i+l:2+i+l+a]]
    def step(state, inputs):
        vals = [0] * (m + 1)
        for k, lit in enumerate(ins):
            vals[lit // 2] = (inputs >> k) & 1
        for k, rec in enumerate(latch):
            vals[rec[0] // 2] = (state >> k) & 1
        def bit(lit):
            return vals[lit // 2] ^ (lit & 1)
        for lhs, x, y in gates:
            vals[lhs // 2] = bit(x) & bit(y)
        return sum(bit(rec[1]) << k for k, rec in enumerate(latch)), bit(out)
    return i, l, step


def wrapper_step(n, update, state, inputs):
    mask = (1 << n) - 1
    r, s, c = state & mask, (state >> n) & mask, state >> (2*n)
    ar = update(r)
    match = int(s != 0 and ar == s)
    bad = int((inputs == 0 and c and match) or (s != 0 and ar == 0))
    if inputs:
        return inputs | inputs << n, bad
    return ar | s << n | ((1-c) * (1-match)) << (2*n), bad


def reachable_safe(n, step):
    todo, seen = deque([0]), {0}
    while todo:
        state = todo.popleft()
        for inputs in range(1 << n):
            nxt, bad = step(state, inputs)
            if bad:
                return False, len(seen)
            if nxt not in seen:
                seen.add(nxt); todo.append(nxt)
    return True, len(seen)


def cycles_are_odd(n, update):
    # Independent finite permutation criterion, including singular maps.
    images = [update(x) for x in range(1 << n)]
    if len(set(images)) != len(images):
        return False
    remaining = set(range(1 << n))
    while remaining:
        start = next(iter(remaining)); x = images[start]; count = 1
        remaining.remove(start)
        while x != start:
            remaining.remove(x); count += 1; x = images[x]
        if count % 2 == 0:
            return False
    return True


def run():
    manifest = json.loads((ROOT / "SOURCE_MANIFEST.json").read_text())
    for record in manifest["files"]:
        raw = (ROOT / "upstream" / record["file"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == record["git_blob_sha1"], "upstream bytes changed: " + record["file"])
    records = []
    raw_transition_checks = 0
    rejections = 0
    def rejected(raw, taps, exponent):
        nonlocal rejections
        try:
            check(raw, taps, exponent)
        except Rejected:
            rejections += 1
            return
        raise RuntimeError("counterfeit accepted")
    files = sorted((ROOT / "upstream").glob("*.aag"))
    for p in files:
        n = int(p.name.split("-")[1]); taps = int(p.stem.split("-")[2], 16)
        raw = p.read_bytes()
        result = check(raw, taps, (1 << n) - 1)
        require(odd_order(n, taps), "source-aware comparator disagrees")
        records.append({"file": p.name, **result, "squarefree_comparator": True})
        rejected(raw, taps ^ 1, (1 << n) - 1)
        rejected(raw, taps, 2 * ((1 << n) - 1))
        rejected(raw, taps, 1)
        if n <= 4:
            _, l, step = raw_model(raw)
            def update(x):
                feedback = sum((x >> i & 1) for i in range(n) if taps >> i & 1) % 2
                return ((x << 1) & ((1 << n)-1)) | feedback
            for state in range(1 << l):
                for inputs in range(1 << n):
                    require(step(state, inputs) == wrapper_step(n, update, state, inputs), "raw wrapper mismatch")
                    raw_transition_checks += 1
            require(reachable_safe(n, step)[0], "raw circuit not safe")
    # Independent theorem checks for ALL binary n*n matrices, n=1,2,3.
    matrix_cases = 0
    for n in (1, 2, 3):
        for entries in range(1 << (n*n)):
            def update(x):
                return sum((sum(((entries >> (i*n+j)) & 1) * ((x >> j) & 1) for j in range(n)) % 2) << i for i in range(n))
            safe, _ = reachable_safe(n, lambda state, inputs: wrapper_step(n, update, state, inputs))
            require(safe == cycles_are_odd(n, update), "odd-order wrapper theorem mismatch")
            matrix_cases += 1
    # Identity is safe (nonmaximal period one); swap has a period-two bad trace.
    require(reachable_safe(2, lambda s, u: wrapper_step(2, lambda x:x, s, u))[0], "identity case")
    require(not reachable_safe(2, lambda s, u: wrapper_step(2, lambda x:((x&1)<<1)|(x>>1), s, u))[0], "swap case")
    companion_cases = 0
    for n in range(2, 6):
        for taps in range(1 << n):
            def update(x):
                return ((x << 1) & ((1 << n)-1)) | ((x & taps).bit_count() % 2)
            require(odd_order(n, taps) == cycles_are_odd(n, update), "squarefree comparator mismatch")
            companion_cases += 1
    p = ROOT / "upstream/fibonacci-04-0xc.aag"
    raw = p.read_bytes(); lines = raw.decode().splitlines(); n = 4; l = 9
    for exp in (True, 0, -1, 1 << 4096):
        rejected(raw, 12, exp)
    for tap in (True, 0, 16, -1):
        rejected(raw, tap, 15)
    mutated = []
    # Wrong result detector, forced counter, changed initial state, and shifted latch.
    a = lines.copy(); a[1+n+l] = "1"; mutated.append(("always_bad", a, True))
    a = lines.copy(); a[1+n+l-1] = a[1+n+l-1].split()[0] + " 1"; mutated.append(("counter_forced_one", a, True))
    a = lines.copy(); a[1+n] += " 1"; mutated.append(("nonzero_initial_state", a, False))
    a = lines.copy(); a[1+n] = a[1+n].split()[0] + " 0"; mutated.append(("zero_first_latch", a, True))
    mutation_results = []
    for name, text, test_unsafe in mutated:
        damaged = ("\n".join(text)+"\n").encode()
        rejected(damaged, 12, 15)
        if test_unsafe:
            _, _, step = raw_model(damaged)
            require(not reachable_safe(4, step)[0], "mutation is not unsafe: "+name)
        mutation_results.append({"name":name,"rejected":True,"raw_counterexample_found":test_unsafe})
    for damaged in (b"", raw[:20], raw.replace(b"aag 67", b"aag 68", 1), raw.replace(b"28 15 16",b"28 28 16",1), raw.replace(b"l0 register_bit_0",b"l0 duplicate\nl0 register_bit_0",1)):
        rejected(damaged, 12, 15)
    # Highly shared malformed DAG: recursive expression tuples used to make
    # this family exponentially expensive to hash. Interned IDs keep it a DAG.
    a = 5000
    shared = [f"aag {7+a} 2 5 1 {a}", "2", "4"]
    shared.extend(f"{2*k} 0" for k in range(3, 8))
    shared.append("0")
    prev, older = 2, 4
    for k in range(8, 8+a):
        lit = 2*k
        shared.append(f"{lit} {prev^1} {older^1}")
        older, prev = prev, lit
    rejected(("\n".join(shared)+"\n").encode(), 3, 3)
    return {"upstream_files_verified":len(manifest["files"]),"circuits":records,"raw_transition_checks":raw_transition_checks,"all_small_binary_matrices":matrix_cases,"small_companion_comparisons":companion_cases,"counterfeit_rejections":rejections,"unsafe_mutations":mutation_results,"identity_and_swap_controls":True}


if __name__ == "__main__":
    checkpoint = json.loads((ROOT / "CHECKPOINT_MANIFEST.json").read_text())
    for name, expected_hash in checkpoint["files"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected_hash,
                "checkpoint source hash changed: " + name)
    result = run()
    expected = json.loads((ROOT / "expected.json").read_text())
    require(result == expected, "deterministic checkpoint changed")
    print("PASS: 23 original AAG circuits; 9,344 independent raw transitions;")
    print("530 small matrix controls, 60 companion controls, and 87 false-proof rejections.")
    print("A scoped source-bound safety proof, not novel algebra or a general frontend.")
