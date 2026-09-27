#!/usr/bin/env python3
"""Execute the existing Certifaiger/CaDiCaL/LRAT pipeline on one candidate.

This is orchestration, not a new certificate format or a replacement proof
checker. Every raw obligation, CNF, completed LRAT trace and log is retained.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path

SECONDS = 10
MEMORY = 1 << 30
ARTIFACT_LIMIT = 64 << 20
OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--witness", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out, tool_dir = args.output.resolve(), args.tools.resolve()
    model, witness = args.model.resolve(), args.witness.resolve()
    if out.exists():
        raise SystemExit("Refusing to overwrite an existing evidence directory")
    tools = {name: tool_dir / name for name in
             ("certifaiger", "aigsplit", "aigtocnf", "cadical", "lrat-trim")}
    if any(not path.is_file() for path in tools.values()):
        raise SystemExit("Missing native executable")
    out.mkdir(parents=True)
    shutil.copyfile(model, out / "model.aag")
    shutil.copyfile(witness, out / "witness.aag")
    record = {
        "schema": 1, "interface": "existing Certifaiger AIGER witness circuits",
        "input_paths": {"model": str(model), "witness": str(witness)},
        "input_sha256": {"model": sha(out / "model.aag"), "witness": sha(out / "witness.aag")},
        "binary_sha256": {name: sha(path) for name, path in tools.items()},
        "limits": {"seconds_per_process": SECONDS, "address_space_bytes": MEMORY,
                   "artifact_bytes_per_case": ARTIFACT_LIMIT},
        "stages": [], "obligations": [], "status": "incomplete",
    }
    started = time.perf_counter()

    def artifact_bytes():
        return sum(path.stat().st_size for path in out.iterdir()
                   if path.suffix in (".aag", ".aig", ".cnf", ".lrat"))

    def save():
        record["elapsed_seconds"] = time.perf_counter() - started
        record["artifact_bytes"] = artifact_bytes()
        (out / "RESULTS.json").write_text(json.dumps(record, indent=2) + "\n")

    def stage(name, argv):
        remaining = ARTIFACT_LIMIT - artifact_bytes()
        if remaining <= 0:
            record["status"] = "unknown"
            record["reason"] = "artifact limit"
            save()
            return None
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
            resource.setrlimit(resource.RLIMIT_FSIZE, (remaining, remaining))
        start = time.perf_counter()
        try:
            result = subprocess.run([str(item) for item in argv], cwd=out,
                                    capture_output=True, timeout=SECONDS,
                                    preexec_fn=limits)
            code, timed_out = result.returncode, False
            stdout, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired as error:
            code, timed_out = None, True
            stdout, stderr = error.stdout or b"", error.stderr or b""
        (out / (name + ".stdout.txt")).write_bytes(stdout)
        (out / (name + ".stderr.txt")).write_bytes(stderr)
        row = {"name": name, "argv": [str(item) for item in argv],
               "exit_code": code, "timed_out": timed_out,
               "elapsed_seconds": time.perf_counter() - start}
        record["stages"].append(row)
        if timed_out or (code is not None and code < 0) or artifact_bytes() > ARTIFACT_LIMIT:
            record["status"] = "unknown"
            record["reason"] = "native timeout/resource limit"
            code = None
        save()
        print(json.dumps(row), flush=True)
        return code

    def failed(reason):
        if record["status"] == "incomplete":
            record["status"] = "error"
            record["reason"] = reason
        save()

    code = stage("generate", [tools["certifaiger"], "model.aag", "witness.aag", "check.aig"])
    if code != 0:
        failed("native witness-obligation generation failed")
        return
    code = stage("split", [tools["aigsplit"], "-n", "check.aig", "obligation_"])
    if code != 0 or not all((out / (name + ".aig")).is_file() for name in OBLIGATIONS):
        failed("native obligation splitting failed or expected output absent")
        return
    for name in OBLIGATIONS:
        row = {"name": name, "status": "incomplete"}
        record["obligations"].append(row)
        code = stage(name + "_cnf", [tools["aigtocnf"], name + ".aig", name + ".cnf"])
        if code != 0:
            failed("CNF conversion failed")
            return
        code = stage(name + "_solve", [tools["cadical"], "--quiet", "--unsat", "--lrat",
                                      "--no-binary", "--no-factor", name + ".cnf", name + ".lrat"])
        if code == 10:
            row["status"], record["status"] = "sat", "rejected"
            record["reason"] = "SAT counterexample to " + name
            save()
            return
        if code != 20:
            failed("UNSAT not established")
            return
        code = stage(name + "_replay", [tools["lrat-trim"], name + ".cnf", name + ".lrat"])
        if code != 20:
            failed("native LRAT replay failed")
            return
        row["status"] = "unsat_replayed"
        row["cnf_sha256"], row["proof_sha256"] = sha(out / (name + ".cnf")), sha(out / (name + ".lrat"))
        row["cnf_bytes"], row["proof_bytes"] = (out / (name + ".cnf")).stat().st_size, (out / (name + ".lrat")).stat().st_size
        save()
    record["status"] = "accepted"
    save()


if __name__ == "__main__":
    main()
