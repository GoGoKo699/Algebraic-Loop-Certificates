"""Freeze, then execute the fixed study; never choose cases from outcomes.

The supervisor starts the total clock before the fresh worker imports or reads
its model. Setup/provenance validation and later archive compression are outside
that clock. Each trial has an exclusive new directory; interrupted evidence is
preserved, and execution refuses to restart an existing trial. Qualification
is a separate experiment and must have passed before a freeze can be created.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = ((2, 0x3), (4, 0xc), (8, 0xb8), (12, 0xe08),
         (16, 0xd008), (24, 0xe10000))
TOOLS = ("ric3", "certifaiger", "aigsplit", "aigtocnf", "cadical", "lrat-trim")
SOURCES = (
    "research/completion_v1/study.py",
    "research/completion_v1/worker.py",
    "research/completion_v1/resources.py",
    "research/completion_v1/verify_qualification.py",
    "research/completion_v1/STUDY_DESIGN.md",
    "research/completion_v1/EXECUTABLE_PROTOCOL.md",
    "research/odd_order_witness_v1/produce.py",
    "research/proof_interface_v1/produce.py",
    "research/proof_interface_v1/lrat.py",
    "research/aiger_lfsr_v1/check.py",
    "research/aiger_lfsr_v1/source_aware.py",
    "research/aiger_lfsr_v1/SOURCE_MANIFEST.json",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def case_records():
    upstream = ROOT / "research/aiger_lfsr_v1/upstream"
    manifest = json.loads((upstream.parent / "SOURCE_MANIFEST.json").read_text())
    blobs = {r["file"]: r["git_blob_sha1"] for r in manifest["files"]}
    result = []
    for width, taps in CASES:
        model = upstream / f"fibonacci-{width:02}-0x{taps:x}.aag"
        raw = model.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if blob != blobs[model.name]:
            raise ValueError("Original upstream blob changed: " + model.name)
        result.append({"width": width, "taps": taps, "odd_multiple": (1 << width)-1,
                       "model": str(model.relative_to(ROOT)), "sha256": sha(model),
                       "git_blob_sha1": blob})
    return result


def trial_order():
    rows = []
    for trial in (1, 2, 3):
        routes = ("exporter", "ric3") if trial % 2 else ("ric3", "exporter")
        for width, _ in CASES:
            for route in (*routes, "structural"):
                rows.append({"id": f"n{width:02}-t{trial}-{route}",
                             "width": width, "trial": trial, "route": route})
    return rows


def worker_command(row, case, tools, output):
    argv = [sys.executable, "-m", "research.completion_v1.worker",
            "--route", row["route"], "--model", str(ROOT / case["model"]),
            "--tools", str(tools), "--output", str(output)]
    if row["route"] in ("exporter", "structural"):
        argv += ["--width", str(case["width"]), "--taps", hex(case["taps"])]
    if row["route"] == "exporter":
        argv += ["--odd-multiple", str(case["odd_multiple"])]
    return argv


def freeze(tools, output):
    from .resources import Limits
    from dataclasses import asdict
    from .verify_qualification import verify_qualification
    if output.exists():
        raise ValueError("Refusing to overwrite a protocol freeze")
    qualification = verify_qualification()
    binary_hashes = {name: sha(tools / name) for name in TOOLS}
    qmanifest = json.loads((HERE / "qualification/MANIFEST.json").read_text())
    if binary_hashes != qmanifest["binary_sha256"]:
        raise ValueError("Tools differ from the qualified executables")
    record = {
        "schema": 1, "kind": "fixed_completion_study_before_measurement",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_files_sha256": {p: sha(ROOT / p) for p in SOURCES},
        "qualification_manifest_sha256": sha(HERE / "qualification/MANIFEST.json"),
        "qualification_summary": qualification,
        "binary_sha256": binary_hashes,
        "python": {"executable": sys.executable, "version": sys.version,
                   "sha256": sha(Path(sys.executable))},
        "environment": {"platform": platform.platform(),
                        "cpu_affinity_available": sorted(os.sched_getaffinity(0)),
                        "cache_policy": "fresh processes; no cache flushing"},
        "limits": asdict(Limits(cpu=min(os.sched_getaffinity(0)))),
        "cases": case_records(), "order": trial_order(),
        "seed": 0,
        "environment_overrides": {"PYTHONHASHSEED": "0", "LC_ALL": "C", "RUST_LOG": "info"},
    }
    write_new(output, record)
    return {"freeze": str(output), "sha256": sha(output), "planned_trials": len(record["order"])}


def validate_freeze(path, tools):
    from .resources import Limits
    from dataclasses import asdict
    record = json.loads(path.read_text())
    if record["schema"] != 1 or record["kind"] != "fixed_completion_study_before_measurement":
        raise ValueError("Unknown protocol freeze")
    for p, expected in record["source_files_sha256"].items():
        if p not in SOURCES or sha(ROOT / p) != expected:
            raise ValueError("Frozen source changed: " + p)
    if set(record["source_files_sha256"]) != set(SOURCES):
        raise ValueError("Incomplete source freeze")
    if record["cases"] != case_records() or record["order"] != trial_order():
        raise ValueError("Frozen cases/order changed")
    cpu = record["limits"].get("cpu")
    if (type(cpu) is not int or cpu not in os.sched_getaffinity(0)
            or record["limits"] != asdict(Limits(cpu=cpu)) or record["seed"] != 0):
        raise ValueError("Frozen resource policy changed")
    if record["environment_overrides"] != {"PYTHONHASHSEED": "0", "LC_ALL": "C", "RUST_LOG": "info"}:
        raise ValueError("Frozen environment policy changed")
    if record["qualification_manifest_sha256"] != sha(HERE / "qualification/MANIFEST.json"):
        raise ValueError("Qualification changed")
    qualification = json.loads((HERE / "qualification/MANIFEST.json").read_text())
    if record["binary_sha256"] != qualification["binary_sha256"]:
        raise ValueError("Frozen executables were not qualified")
    if record["binary_sha256"] != {name: sha(tools / name) for name in TOOLS}:
        raise ValueError("Frozen executable changed")
    if record["python"] != {"executable": sys.executable, "version": sys.version,
                            "sha256": sha(Path(sys.executable))}:
        raise ValueError("Frozen Python runtime changed")
    return record


def archive_trial(directory):
    """Compress only after stopping the measured workflow; preserve raw hashes."""
    records = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        raw = path.read_bytes()
        logical = str(path.relative_to(directory))
        if len(raw) > 65536:
            stored = path.with_name(path.name + ".gz")
            with stored.open("xb") as stream:
                stream.write(gzip.compress(raw, mtime=0))
            path.unlink()
            encoding = "gzip"
        else:
            stored, encoding = path, "raw"
        records[logical] = {"stored_path": str(stored.relative_to(directory)),
                            "encoding": encoding, "raw_bytes": len(raw),
                            "raw_sha256": hashlib.sha256(raw).hexdigest(),
                            "stored_bytes": stored.stat().st_size, "stored_sha256": sha(stored)}
    write_new(directory / "ARTIFACTS.json", records)


def retained_log_conflict(directory, observation):
    """Honor definitive failures retained before a worker journal update.

    A deadline can interrupt the few instructions between native output, stage
    finish logging, and the atomic worker journal. Complete retained verdicts
    still take precedence. An incomplete trailing JSONL record is not a verdict.
    """
    data = directory / "data"
    for log in data.glob("*_solve.stdout.txt"):
        if "s SATISFIABLE" in log.read_text(errors="replace").splitlines():
            return True
    ric3_log = data / "ric3.stdout.txt"
    if ric3_log.exists():
        verdicts = [line.strip() for line in ric3_log.read_text(errors="replace").splitlines()
                    if line.strip() in ("SAT", "UNSAT", "UNKNOWN")]
        if verdicts and verdicts != ["UNSAT"]:
            return True
    stages = data / "STAGES.jsonl"
    if stages.exists():
        lines = stages.read_text().splitlines(keepends=True)
        for index, line in enumerate(lines):
            try:
                process = json.loads(line)
            except json.JSONDecodeError:
                if index == len(lines)-1 and not line.endswith("\n"):
                    break
                return True
            if process.get("event") != "finish":
                continue
            tool = Path(process["command"][0]).name
            expected_exit = 20 if tool in ("cadical", "lrat-trim") else 0
            if (process.get("status") == "completed" and
                    process.get("resource_signal") == "file_size_limit" and
                    observation.get("reason") == "artifact_limit"):
                continue
            if process.get("status") != "completed" or process.get("exit_code") != expected_exit:
                return True
    return False


def execute(path, tools, output):
    from .resources import Limits, run_workflow
    record = validate_freeze(path, tools)
    if output.exists():
        raise ValueError("Refusing to repeat or overwrite a study run")
    output.mkdir(parents=True)
    write_new(output / "PROTOCOL_COPY.json", record)
    case_map = {c["width"]: c for c in record["cases"]}
    # There is intentionally no selection or restart option after seeing results.
    for row in record["order"]:
        directory = output / row["id"]
        directory.mkdir()
        command = worker_command(row, case_map[row["width"]], tools, directory / "data")
        env = dict(os.environ, PYTHONPATH=str(ROOT), **record["environment_overrides"])
        try:
            observation = run_workflow(command, cwd=ROOT, artifact_root=directory, env=env,
                                       limits=Limits(**record["limits"]))
        except Exception as error:
            write_new(output / "SUSPENDED.json", {
                "trial": row["id"], "reason": "Supervisor infrastructure failure",
                "error": type(error).__name__ + ": " + str(error),
                "rule": "No performance conclusion or automatic restart"})
            raise
        write_new(directory / "SUPERVISOR.json", observation)
        result_path = directory / "data/RESULT.json"
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        journal_path = directory / "data/JOURNAL.json"
        journal = json.loads(journal_path.read_text()) if journal_path.exists() else None
        print(json.dumps({"trial": row["id"], "supervisor_status": observation["status"],
                          "worker_status": result["status"] if result else None}), flush=True)
        expected = "structural_accepted" if row["route"] == "structural" else "accepted"
        normal = (observation["status"] == "completed" and result is not None
                  and result["route"] == row["route"] and result["status"] == expected)
        evidence = result if result is not None else journal
        conflict = retained_log_conflict(directory, observation)
        if evidence is not None:
            state_conflict = evidence.get("status") not in ("incomplete", expected)
            # A native file-size signal is attributable only alongside actual
            # observed aggregate raw excess, never from the signal alone.
            if (evidence.get("status") == "unknown" and
                    evidence.get("resource_cause") == "file_size_limit" and
                    observation.get("reason") == "artifact_limit"):
                state_conflict = False
            conflict |= state_conflict
            if evidence.get("route", row["route"]) != row["route"]:
                conflict = True
            for obligation in evidence.get("obligations", []):
                if obligation.get("status") == "sat":
                    conflict = True
            for phase in evidence.get("phases", []):
                process = phase.get("process")
                if process is None:
                    if phase.get("status") == "failed":
                        conflict = True
                    continue
                file_limit = (process.get("status") == "completed" and
                              process.get("resource_signal") == "file_size_limit" and
                              observation.get("reason") == "artifact_limit")
                required_exit = 20 if phase["name"].endswith(("_solve", "_replay")) else 0
                if not file_limit and (process.get("status") != "completed" or
                                       process.get("exit_code") != required_exit):
                    conflict = True
        limited = (observation["status"] == "resource_limit"
                   and observation.get("reason") in ("deadline", "artifact_limit")
                   and set(observation.get("observed_violations", [])) <= {"deadline", "artifact_limit"}
                   and not conflict)
        normal = normal and not conflict and not observation.get("observed_violations")
        archive_trial(directory)
        if not (normal or limited):
            write_new(output / "SUSPENDED.json", {
                "trial": row["id"], "reason": "Execution/correctness issue requires investigation",
                "supervisor_status": observation["status"],
                "worker_status": result["status"] if result else None,
                "rule": "No performance conclusion or automatic restart after suspension"})
            raise ValueError("Study suspended; retain every artifact and investigate " + row["id"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "execute"))
    parser.add_argument("--tools", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--freeze", type=Path, default=HERE / "PROTOCOL_FREEZE.json")
    args = parser.parse_args()
    if args.mode == "freeze":
        print(json.dumps(freeze(args.tools.resolve(), args.output.resolve()), indent=2))
    else:
        execute(args.freeze.resolve(), args.tools.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
