#!/usr/bin/env python3
"""Replay the preregistered six-case native ABC PDR baseline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import re
import signal
import subprocess
import time


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def restrict():
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))


def same_transition_structure(left, right):
    """Exact AND DAG equality up to gate numbering and commutative fanin order.

    Compare input/latch positions, reset values, next-state cones and outputs.
    This accepts the converter's reencoding but no Boolean simplification.
    Shared integer interning uses tuple equality, not probabilistic hashes.
    """
    intern = {}

    def token(key):
        if key not in intern:
            intern[key] = len(intern)
        return intern[key]

    def canonical(path):
        lines = path.read_text().splitlines()
        header = lines[0].split()
        require(header[0] == "aag" and len(header) == 6, "Expected basic AAG header")
        _, ninputs, nlatches, noutputs, nands = map(int, header[1:])
        at = 1
        atoms = {0: token(("constant", 0))}
        for i in range(ninputs):
            v = int(lines[at]); at += 1
            require(v > 0 and not v % 2 and v // 2 not in atoms, "Malformed input")
            atoms[v // 2] = token(("input", i))
        latches = []
        for i in range(nlatches):
            parts = list(map(int, lines[at].split())); at += 1
            require(len(parts) in (2, 3) and parts[0] > 0 and not parts[0] % 2 and parts[0] // 2 not in atoms, "Malformed latch")
            atoms[parts[0] // 2] = token(("latch", i))
            init = parts[2] if len(parts) == 3 else 0
            require(init in (0, 1), "This fixed corpus has determinate initial states")
            latches.append((parts[1], init))
        outputs = [int(x) for x in lines[at:at+noutputs]]; at += noutputs

        def literal(v):
            return 2 * atoms[v // 2] + v % 2

        for line in lines[at:at+nands]:
            lhs, a, b = map(int, line.split())
            require(lhs > 0 and not lhs % 2 and lhs // 2 not in atoms, "Malformed gate")
            atoms[lhs // 2] = token(("and", *sorted((literal(a), literal(b)))))
        return (ninputs, nlatches, noutputs, tuple((literal(v), init) for v, init in latches), tuple(map(literal, outputs)))

    return canonical(left) == canonical(right)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--abc", type=Path, required=True)
    ap.add_argument("--aigtoaig", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    for k in ["upstream", "abc", "aigtoaig", "out"]:
        setattr(args, k, getattr(args, k).resolve())
    provenance = json.loads((Path(__file__).with_name("native") / "TOOL_PROVENANCE.json").read_text())
    for name in ("abc", "aigtoaig"):
        binary = getattr(args, name)
        require(sha256(binary) == provenance[name]["binary_sha256"], f"Pinned {name} binary mismatch")
        actual = subprocess.check_output(["git", "-C", str(binary.parent), "rev-parse", "HEAD"], text=True).strip()
        require(actual == provenance[name]["commit"], f"Pinned {name} source mismatch")
        subprocess.run(["git", "-C", str(binary.parent), "diff", "--exit-code", "HEAD", "--"], check=True, stdout=subprocess.DEVNULL)
    source_manifest = json.loads((Path(__file__).with_name("SOURCE_MANIFEST.json")).read_text())
    require(source_manifest["commit"] == "c8efd0251c0548dd46168db8410e6777c5f82b73", "Upstream pin mismatch")
    source_blobs = {entry["file"]: entry["git_blob_sha1"] for entry in source_manifest["files"]}
    args.out.mkdir(parents=True, exist_ok=False)
    results = []
    for n in (2, 4, 8, 12, 16, 24):
        matches = list(args.upstream.glob(f"fibonacci-{n:02d}-*.aag"))
        require(len(matches) == 1, f"Expected one input for width {n}")
        original = matches[0]
        data = original.read_bytes()
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        require(blob == source_blobs[original.name], f"Upstream source hash mismatch: {original.name}")
        binary = args.out / original.with_suffix(".aig").name
        converted = subprocess.run([str(args.aigtoaig), str(original), str(binary)], capture_output=True, check=True)
        (args.out / f"n{n:02d}-conversion.stdout").write_bytes(converted.stdout)
        (args.out / f"n{n:02d}-conversion.stderr").write_bytes(converted.stderr)
        roundtrip = args.out / original.name
        subprocess.run([str(args.aigtoaig), str(binary), str(roundtrip)], capture_output=True, check=True)
        require(same_transition_structure(original, roundtrip), f"AIGER roundtrip structure changed: {original.name}")
        script = f"read_aiger {binary}; pdr -S 91648253; print_status"
        cmd = ["/usr/bin/stdbuf", "-oL", "-eL", str(args.abc), "-s", "-c", script]
        started = time.monotonic()
        timed_out = False
        stdout_path = args.out / f"n{n:02d}.stdout"
        stderr_path = args.out / f"n{n:02d}.stderr"
        with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
            proc = subprocess.Popen(cmd, stdout=out, stderr=err, preexec_fn=restrict, start_new_session=True)
            while True:
                waited, waitstatus, usage = os.wait4(proc.pid, os.WNOHANG)
                if waited:
                    break
                if time.monotonic() - started >= 10:
                    timed_out = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    _, waitstatus, usage = os.wait4(proc.pid, 0)
                    break
                time.sleep(0.01)
            proc.returncode = os.waitstatus_to_exitcode(waitstatus)
        elapsed = time.monotonic() - started
        output = stdout_path.read_text(errors="replace")
        timing = {"user_seconds": usage.ru_utime, "system_seconds": usage.ru_stime, "max_rss_kib": usage.ru_maxrss, "wall_seconds": elapsed, "timeout_killed_by_harness": timed_out}
        (args.out / f"n{n:02d}-time.json").write_text(json.dumps(timing, indent=2) + "\n")
        if timed_out:
            status = "wall_timeout_unknown"
        elif proc.returncode != 0:
            status = "process_error"
        elif re.search(r"^Status = 1\s", output, re.M):
            status = "solver_reported_safe"
        elif re.search(r"^Status = 0\s", output, re.M):
            status = "solver_reported_unsafe"
        else:
            status = "no_decisive_status"
        results.append({"n": n, "input_filename": original.name, "input_sha256": sha256(original), "binary_filename": binary.name, "binary_sha256": sha256(binary), "roundtrip_sha256": sha256(roundtrip), "aiger_roundtrip_identical_transition_structure": True, "command": cmd, "returncode": proc.returncode, "wall_seconds_including_wrapper": elapsed, "status": status})
        report = {"plan_sha256": sha256(Path(__file__).with_name("native") / "PLAN.json"), "abc_binary_sha256": sha256(args.abc), "aigtoaig_binary_sha256": sha256(args.aigtoaig), "runner_sha256": sha256(Path(__file__)), "results": results}
        (args.out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(results[-1]), flush=True)


if __name__ == "__main__":
    main()
