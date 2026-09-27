#!/usr/bin/env python3
"""Build pinned tools and qualify a tiny witness; NEVER a benchmark runner.

No solver/checker source is patched. Build/setup and compatibility observations
are retained separately from the fixed comparison, which remains unexecuted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from research.proof_interface_v1.lrat import check_lrat

PINS = {
    "ric3": ("gipsyh/rIC3", "8dcec6995e0e5c0adf7d4397047aafc06e9559dc"),
    "certifaiger": ("Froleyks/certifaiger", "27d526e3e979074c3e92582768f577dc6eddb0da"),
    "aiger": ("arminbiere/aiger", "039ec1a2cc37d3093ac35c4b6df65336b346f409"),
    "cadical": ("arminbiere/cadical", "c60730422e758ef1cebe7aeddf2dda31c996bf04"),
    "lrat-trim": ("arminbiere/lrat-trim", "adba6e61368e91957c79bf952b29800f05dbee51"),
}
OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")
MODEL_NAMES = {2: "fibonacci-02-0x3.aag", 4: "fibonacci-04-0xc.aag"}
MODEL_BLOBS = {2: "492d5e8ed0f745bb32b9074893cf27d7bf42805a",
               4: "908ebd7b513afa29385671c07e71167eaf1df90d"}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def inspect_case(directory, rejected_at=None):
    """Check actual native observations and independently replay completed CNFs."""
    record = json.loads((directory / "RESULTS.json").read_text())
    names = OBLIGATIONS if rejected_at is None else OBLIGATIONS[:OBLIGATIONS.index(rejected_at) + 1]
    require(record["status"] == ("accepted" if rejected_at is None else "rejected"),
            "Unexpected native verdict")
    require(tuple(row["name"] for row in record["obligations"]) == names,
            "Missing, duplicated or reordered obligations")
    require(record["input_sha256"] == {k: sha(directory / (k + ".aag"))
                                      for k in ("model", "witness")}, "Input hash mismatch")
    expected = [("generate", 0), ("split", 0)]
    for name in names:
        expected += [(name + "_cnf", 0), (name + "_solve", 10 if name == rejected_at else 20)]
        if name != rejected_at:
            expected.append((name + "_replay", 20))
    require([(row["name"], row["exit_code"]) for row in record["stages"]] == expected,
            "Incomplete native command/exit-code sequence")
    require(all(not row["timed_out"] for row in record["stages"]), "Native timeout")
    replays = []
    for row in record["obligations"]:
        name = row["name"]
        if name == rejected_at:
            require(row["status"] == "sat", "Missing negative-control SAT rejection")
            require(b"s SATISFIABLE" in (directory / (name + "_solve.stdout.txt")).read_bytes(),
                    "Missing SAT log")
            continue
        require(row["status"] == "unsat_replayed", "Unreplayed native obligation")
        require(row["cnf_sha256"] == sha(directory / (name + ".cnf")) and
                row["proof_sha256"] == sha(directory / (name + ".lrat")), "Proof hash mismatch")
        checked = check_lrat(directory / (name + ".cnf"), directory / (name + ".lrat"))
        require(checked["status"] == "verified_unsat", "Independent Python replay failed")
        replays.append({"obligation": name, "result": checked})
    return {"status": record["status"], "rejected_at": rejected_at,
            "independent_replays": replays, "native_result_sha256": sha(directory / "RESULTS.json")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    work, out = args.work.resolve(), args.output.resolve()
    require(not work.exists() and not out.exists(), "Refusing to overwrite build or evidence")
    work.mkdir(parents=True)
    out.mkdir(parents=True)
    logs, tools = out / "logs", work / "bin"
    logs.mkdir()
    tools.mkdir()
    started = time.monotonic()
    record = {"schema": 1, "purpose": "tiny compatibility qualification, not benchmark evidence",
              "status": "blocked", "commands": [], "sources": {}, "cases": [],
              "environment": {"platform": platform.platform(), "python": sys.version,
                              "cpu_affinity": sorted(os.sched_getaffinity(0)),
                              "github_run_id": os.environ.get("GITHUB_RUN_ID"),
                              "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT")},
              "qualification_limits": {"native_driver_seconds_per_process": 10,
                    "outer_smoke_seconds": 120, "address_space_per_process_bytes": 1 << 30,
                    "cpu_affinity_count": 1,
                    "note": "Not the common 30-second end-to-end experiment protocol"},
              "script_sha256": sha(Path(__file__))}

    def save():
        record["setup_and_qualification_elapsed_seconds"] = time.monotonic() - started
        (out / "QUALIFICATION.json").write_text(json.dumps(record, indent=2) + "\n")

    def run(label, argv, cwd=work, seconds=900, limited=False):
        argv = list(map(str, argv))
        print(label + ": " + " ".join(argv), flush=True)
        start = time.monotonic()
        row = {"label": label, "argv": argv, "cwd": str(cwd), "deadline_seconds": seconds,
               "limited_smoke": limited, "exit_code": None, "timed_out": False}
        record["commands"].append(row)
        save()

        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
            resource.setrlimit(resource.RLIMIT_FSIZE, (64 << 20, 64 << 20))
            os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})

        with (logs / (label + ".stdout.txt")).open("wb") as stdout, \
                (logs / (label + ".stderr.txt")).open("wb") as stderr:
            proc = subprocess.Popen(argv, cwd=cwd, stdout=stdout, stderr=stderr,
                                    start_new_session=True,
                                    preexec_fn=limits if limited else None)
            try:
                row["exit_code"] = proc.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                row["timed_out"] = True
            finally:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
                row["elapsed_seconds"] = time.monotonic() - start
                save()
        if row["exit_code"] != 0 or row["timed_out"]:
            for stream in ("stdout", "stderr"):
                print((logs / (label + "." + stream + ".txt")).read_text(errors="replace")[-12000:])
            raise RuntimeError("Qualification setup/execution blocked at " + label)
        return (logs / (label + ".stdout.txt")).read_text(errors="replace")

    try:
        record["repository_commit"] = run("repository-head", ["git", "rev-parse", "HEAD"], ROOT).strip()
        record["repository_tracked_status"] = run("repository-status", ["git", "status", "--porcelain", "--untracked-files=no"], ROOT)
        require(not record["repository_tracked_status"], "Tracked repository changes before qualification")
        for name, command in (("cc", ["gcc", "--version"]), ("cxx", ["g++", "--version"]),
                              ("rust", ["rustc", "-Vv"]), ("cargo", ["cargo", "-Vv"]),
                              ("cmake", ["cmake", "--version"]), ("meson", ["meson", "--version"])):
            record["environment"][name] = run("version-" + name, command)
        for name, (repo, commit) in PINS.items():
            source = work / name
            source.mkdir()
            run(name + "-init", ["git", "init"], source)
            run(name + "-remote", ["git", "remote", "add", "origin", "https://github.com/" + repo + ".git"], source)
            run(name + "-fetch", ["git", "fetch", "--depth=1", "origin", commit], source)
            run(name + "-checkout", ["git", "checkout", "--detach", "FETCH_HEAD"], source)
            head = run(name + "-head", ["git", "rev-parse", "HEAD"], source).strip()
            require(head == commit, "Source commit mismatch")
            record["sources"][name] = {"repository": repo, "commit": head,
                "tree": run(name + "-tree", ["git", "rev-parse", "HEAD^{tree}"], source).strip()}
        ric3 = work / "ric3"
        run("ric3-submodules", ["git", "submodule", "update", "--init", "--recursive"], ric3)
        record["sources"]["ric3"]["recursive_submodules"] = run("ric3-submodule-status", ["git", "submodule", "status", "--recursive"], ric3)
        require((ric3 / "Cargo.lock").is_file(), "Pinned source lacks Cargo.lock")
        shutil.copyfile(ric3 / "Cargo.lock", out / "Cargo.lock")
        record["cargo_lock_sha256"] = sha(out / "Cargo.lock")
        run("ric3-build", ["cargo", "build", "--locked", "--release", "--jobs", "2"], ric3, seconds=1200)
        require(sha(ric3 / "Cargo.lock") == record["cargo_lock_sha256"], "Dependency lock changed")
        run("ric3-metadata", ["cargo", "metadata", "--locked", "--format-version", "1"], ric3)
        shutil.copyfile(ric3 / "target/release/ric3", tools / "ric3")
        aiger = work / "aiger"
        run("aiger-object", ["gcc", "-O2", "-c", aiger / "aiger.c", "-o", tools / "aiger.o"])
        run("certifaiger-build", ["g++", "-std=c++23", "-O2", '-DGITID="' + PINS["certifaiger"][1] + '"',
            '-DVERSION="10.3.0"', "-I", aiger, work / "certifaiger/src/certifaiger.cpp",
            tools / "aiger.o", "-o", tools / "certifaiger"])
        for name in ("aigsplit", "aigtocnf"):
            run(name + "-build", ["gcc", "-O2", aiger / (name + ".c"), tools / "aiger.o", "-o", tools / name])
        run("cadical-configure", ["./configure"], work / "cadical")
        run("cadical-build", ["make", "-j2"], work / "cadical")
        shutil.copyfile(work / "cadical/build/cadical", tools / "cadical")
        run("lrat-trim-build", ["gcc", "-O2", work / "lrat-trim/lrat-trim.c", "-o", tools / "lrat-trim"])
        for name in PINS:
            status = run(name + "-tracked-status", ["git", "status", "--porcelain", "--untracked-files=no", "--ignore-submodules=untracked"], work / name)
            record["sources"][name]["tracked_status_after_build"] = status
            require(not status, "Build changed tracked source: " + name)
        run("ric3-recursive-clean", ["git", "submodule", "foreach", "--recursive", "git diff --exit-code; git diff --cached --exit-code"], ric3)
        record["binary_sha256"] = {name: sha(tools / name) for name in
                                   ("ric3", "certifaiger", "aigsplit", "aigtocnf", "cadical", "lrat-trim")}
        run("ric3-help", [tools / "ric3", "--help"])
        run("ric3-check-help", [tools / "ric3", "check", "--help"])
        upstream = ROOT / "research/aiger_lfsr_v1/upstream"
        models = {width: upstream / name for width, name in MODEL_NAMES.items()}
        for width, model in models.items():
            raw = model.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == MODEL_BLOBS[width], "Smoke model differs from pinned original")
        run("ric3-ic3-help", [tools / "ric3", "check", models[2], "ic3", "--help"])
        witness = out / "ric3-smoke.aag"
        verdict = run("ric3-smoke", [tools / "ric3", "check", models[2], "--cert", witness,
                      "--ui", "false", "ic3"], seconds=120, limited=True)
        require("UNSAT" in verdict.splitlines(), "No conclusive safe verdict from rIC3")
        require(witness.is_file() and witness.stat().st_size > 0, "No exported rIC3 witness")
        native = ROOT / "research/proof_interface_v1/native"
        cases = [("ric3-smoke", 2, witness, None),
                 ("positive-history", 2, native / "phase02/witness.aag", None),
                 ("bad-zero", 2, native / "bad_zero02/witness.aag", "Safety"),
                 ("reset-flipped", 2, native / "reset_flipped02/witness.aag", "Reset"),
                 ("freeze-phase", 4, native / "freeze_phase04/witness.aag", "Inductive"),
                 ("inverted-phase", 4, native / "inverted_phase04/witness.aag", "Inductive")]
        for label, width, candidate, rejection in cases:
            destination = out / label
            run(label + "-native", [sys.executable, ROOT / "research/proof_interface_v1/run_native.py",
                "--tools", tools, "--model", models[width], "--witness", candidate,
                "--output", destination], seconds=120, limited=True)
            check_start = time.monotonic()
            result = inspect_case(destination, rejection)
            result.update({"case": label, "offline_python_replay_seconds": time.monotonic() - check_start})
            record["cases"].append(result)
            save()
        record["status"] = "qualified"
        record["comparison_status"] = "not executed; enforcing common-budget harness and protocol freeze still required"
        print("QUALIFIED: rIC3 witness and positive control accepted; all four negative controls rejected.")
    except Exception as error:
        record["blocker"] = {"type": type(error).__name__, "message": str(error)}
        print("BLOCKED:", str(error), flush=True)
    finally:
        save()
        artifacts = {}
        for path in sorted(out.rglob("*")):
            if path.is_file() and path.name != "ARTIFACTS.json":
                artifacts[str(path.relative_to(out))] = {"bytes": path.stat().st_size, "sha256": sha(path)}
        (out / "ARTIFACTS.json").write_text(json.dumps(artifacts, indent=2) + "\n")
    return 0 if record["status"] == "qualified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
