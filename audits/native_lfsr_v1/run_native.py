#!/usr/bin/env python3
"""Replay eight frozen upstream cases; no source changes or network operations."""
import argparse
import hashlib
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

PIN = "20f3adab3121b4205a12f06746055551e6504648"
CASES = [
    ("shr3", "shr3", [], "maximal"),
    ("xoroshiro128pp", "xoroshiro128pp", [], "maximal"),
    ("xoshiro256pp", "xoshiro256pp", [], "maximal"),
    ("xorrot32_default", "xorrot32", [], "maximal"),
    ("xorrot32_bad1", "xorrot32", ["--param=bad1"], "not_maximal"),
    ("xorrot32_bad2", "xorrot32", ["--param=bad2"], "not_maximal"),
    ("splitmix", "splitmix", [], "unsupported"),
    ("sfc64", "sfc64", [], "unsupported"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(command, cwd):
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="Built upstream checkout at the exact frozen commit")
    parser.add_argument("--output", type=Path, required=True,
                        help="New evidence directory; existing paths are refused")
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if capture(["git", "rev-parse", "HEAD"], source) != PIN:
        raise SystemExit("Source HEAD differs from the frozen native baseline")
    if capture(["git", "status", "--porcelain", "--untracked-files=no"], source):
        raise SystemExit("Tracked upstream source is modified")
    if output.exists():
        raise SystemExit("Refusing to overwrite existing evidence")
    executable = source / "bin/smokerand"
    generators = sorted({item[1] for item in CASES})
    artifacts = [executable] + [source / "bin/generators" / (g + ".so") for g in generators]
    artifact_hashes = {str(p.relative_to(source)): digest(p) for p in artifacts}
    output.mkdir(parents=True)
    report = {
        "schema": "alc-native-lfsr-gate-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": "https://github.com/alvoskov/SmokeRand",
        "source_commit": PIN,
        "source_tree": capture(["git", "rev-parse", "HEAD^{tree}"], source),
        "tracked_source_clean": True,
        "source_path": str(source),
        "compiler": capture(["gcc", "--version"], source).splitlines()[0],
        "make_version": capture(["make", "--version"], source).splitlines()[0],
        "platform": platform.platform(),
        "build_command": ["make", "-f", "Makefile.gnu", "-j2", "bin/smokerand"] + ["bin/generators/" + g + ".so" for g in generators],
        "build_time_measured": False,
        "build_note": "The first upstream build completed before this runner; its stdout/stderr were preserved separately. No compile-time speed claim.",
        "artifact_sha256": artifact_hashes,
        "timeout_seconds_per_case": 60,
        "timing_scope": "Single process wall time including upstream initialization, probing, algebra, and output; not a matched ALC timing comparison.",
        "cases": [],
    }
    for name, gen, extra, expectation in CASES:
        command = ["./smokerand", "lfsr", "generators/" + gen + ".so"] + extra
        start = time.perf_counter()
        try:
            result = subprocess.run(command, cwd=source / "bin", capture_output=True, timeout=60)
            stdout, stderr = result.stdout, result.stderr
            returncode, timed_out = result.returncode, False
        except subprocess.TimeoutExpired as error:
            stdout, stderr = error.stdout or b"", error.stderr or b""
            returncode, timed_out = None, True
        elapsed = time.perf_counter() - start
        outpath, errpath = output / (name + ".stdout.txt"), output / (name + ".stderr.txt")
        outpath.write_bytes(stdout)
        errpath.write_bytes(stderr)
        row = {"name": name, "command": command, "expected_upstream_class": expectation,
               "returncode": returncode, "timed_out": timed_out, "elapsed_seconds": elapsed,
               "stdout_file": outpath.name, "stdout_sha256": digest(outpath),
               "stderr_file": errpath.name, "stderr_sha256": digest(errpath)}
        report["cases"].append(row)
        (output / "RESULTS.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(row), flush=True)
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (output / "RESULTS.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
