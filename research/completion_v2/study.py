"""Prospectively freeze a fresh comparison after the storage-policy amendment.

The suspended v1 experiment remains separate evidence. This runner imports its
unchanged worker, cases, order, and archive handling, but uses the v2 supervisor
with independent raw-artifact and metadata budgets. No resume or selected-trial
mode exists; definitive failures and metadata excess always suspend the run.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys

from research.completion_v1.study import (
    SOURCES as PRIOR_SOURCES, TOOLS, archive_trial, case_records,
    retained_log_conflict, sha, trial_order, worker_command, write_new,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR_FREEZE = "research/completion_v1/PROTOCOL_FREEZE.json"
PRIOR_ARCHIVE = "research/completion_v1/study_20260927.tar.xz.parts/manifest.json"
PRIOR_QUALIFICATION = "research/completion_v1/qualification/MANIFEST.json"
SOURCES = (*PRIOR_SOURCES, PRIOR_FREEZE, PRIOR_ARCHIVE, PRIOR_QUALIFICATION,
           "research/completion_v2/resources.py",
           "research/completion_v2/study.py",
           "research/completion_v2/verify_qualification.py",
           "research/completion_v2/STORAGE_AMENDMENT.md",
           "research/completion_v2/EXECUTABLE_PROTOCOL.md")
KIND = "fixed_completion_study_storage_amendment_before_measurement"
ENVIRONMENT = {"PYTHONHASHSEED": "0", "LC_ALL": "C", "RUST_LOG": "info"}
RESTART_POLICY = "fresh_complete_sequence_only; never pool with suspended v1 trials"


def prior_protocol():
    """Require the unchanged source and scientific design of the v1 freeze."""
    record = json.loads((ROOT / PRIOR_FREEZE).read_text())
    if record["schema"] != 1 or record["kind"] != "fixed_completion_study_before_measurement":
        raise ValueError("Unknown prior protocol freeze")
    if set(record["source_files_sha256"]) != set(PRIOR_SOURCES):
        raise ValueError("Incomplete prior source freeze")
    for path, expected in record["source_files_sha256"].items():
        if sha(ROOT / path) != expected:
            raise ValueError("Prior frozen source changed: " + path)
    if record["cases"] != case_records() or record["order"] != trial_order():
        raise ValueError("Prior cases/order changed")
    qualification_path = ROOT / PRIOR_QUALIFICATION
    if record["qualification_manifest_sha256"] != sha(qualification_path):
        raise ValueError("Prior qualification changed")
    if record["binary_sha256"] != json.loads(qualification_path.read_text())["binary_sha256"]:
        raise ValueError("Prior executables differ from qualification")
    if record["seed"] != 0 or record["environment_overrides"] != ENVIRONMENT:
        raise ValueError("Prior seed/environment policy changed")
    return record


def amended_limits(prior):
    """Only add a separate 64 MiB metadata budget to the prior scalar limits."""
    from .resources import Limits
    cpu = prior["limits"].get("cpu")
    if type(cpu) is not int or cpu not in os.sched_getaffinity(0):
        raise ValueError("The prior CPU is unavailable")
    limits = asdict(Limits(cpu=cpu))
    if limits.pop("metadata_bytes") != 64 << 20 or limits != prior["limits"]:
        raise ValueError("Amendment changed a resource limit beyond metadata accounting")
    return asdict(Limits(cpu=cpu))


def history_bindings():
    return {"prior_protocol_freeze": {"path": PRIOR_FREEZE, "sha256": sha(ROOT / PRIOR_FREEZE)},
            "prior_study_archive_manifest": {"path": PRIOR_ARCHIVE, "sha256": sha(ROOT / PRIOR_ARCHIVE)},
            "restart_policy": RESTART_POLICY}


def freeze(tools, output):
    if output.exists():
        raise ValueError("Refusing to overwrite a protocol freeze")
    from .verify_qualification import verify_qualification
    prior = prior_protocol()
    limits = amended_limits(prior)
    qualification = verify_qualification()
    manifest_path = HERE / "qualification/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    binary_hashes = {name: sha(tools / name) for name in TOOLS}
    if binary_hashes != manifest["binary_sha256"] or binary_hashes != prior["binary_sha256"]:
        raise ValueError("Tools differ from the previously and newly qualified executables")
    record = {
        "schema": 2, "kind": KIND,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_files_sha256": {path: sha(ROOT / path) for path in SOURCES},
        "qualification_manifest_sha256": sha(manifest_path),
        "qualification_summary": qualification,
        "binary_sha256": binary_hashes,
        "python": {"executable": sys.executable, "version": sys.version,
                   "sha256": sha(Path(sys.executable))},
        "environment": {"platform": platform.platform(),
                        "cpu_affinity_available": sorted(os.sched_getaffinity(0)),
                        "cache_policy": "fresh processes; no cache flushing"},
        "limits": limits, "cases": case_records(), "order": trial_order(),
        "seed": 0, "environment_overrides": ENVIRONMENT,
        **history_bindings(),
    }
    write_new(output, record)
    return {"freeze": str(output), "sha256": sha(output), "planned_trials": len(record["order"])}


def validate_freeze(path, tools):
    record = json.loads(path.read_text())
    if record["schema"] != 2 or record["kind"] != KIND:
        raise ValueError("Unknown amended protocol freeze")
    if set(record["source_files_sha256"]) != set(SOURCES):
        raise ValueError("Incomplete amended source freeze")
    for source, expected in record["source_files_sha256"].items():
        if sha(ROOT / source) != expected:
            raise ValueError("Frozen source changed: " + source)
    prior = prior_protocol()
    for key, expected in history_bindings().items():
        if record.get(key) != expected:
            raise ValueError("Prior experiment or fresh-run requirement changed: " + key)
    if record["cases"] != case_records() or record["order"] != trial_order():
        raise ValueError("Frozen cases/order changed")
    if record["limits"] != amended_limits(prior) or record["seed"] != 0:
        raise ValueError("Frozen amended resource policy changed")
    if record["environment_overrides"] != ENVIRONMENT:
        raise ValueError("Frozen environment policy changed")
    manifest_path = HERE / "qualification/MANIFEST.json"
    if record["qualification_manifest_sha256"] != sha(manifest_path):
        raise ValueError("Amended qualification changed")
    qualification = json.loads(manifest_path.read_text())
    if (record["binary_sha256"] != qualification["binary_sha256"] or
            record["binary_sha256"] != prior["binary_sha256"]):
        raise ValueError("Frozen executables were not qualified under both policies")
    if record["binary_sha256"] != {name: sha(tools / name) for name in TOOLS}:
        raise ValueError("Frozen executable changed")
    if record["python"] != {"executable": sys.executable, "version": sys.version,
                            "sha256": sha(Path(sys.executable))}:
        raise ValueError("Frozen Python runtime changed")
    return record


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
        metadata_excess = (observation.get("reason") == "metadata_limit" or
                           "metadata_limit" in observation.get("observed_violations", []))
        limited = limited and not metadata_excess
        normal = normal and not conflict and not metadata_excess and not observation.get("observed_violations")
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
