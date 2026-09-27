"""Offline evidence audit for the fresh amended comparison, without v1 pooling.

The prospective v2 freeze fixes one full 54-trial sequence and binds the prior
suspended experiment. This verifier reuses unchanged byte/archive and CNF-proof
primitives, while independently checking v2's separate raw and metadata budgets.
Only the known metadata paths receive the metadata allowance. All other retained
files are raw. Any metadata excess is an execution issue, including simultaneous
raw/time exhaustion. Accepted witness trials require all nine native replays and
independent CNF proof replay. Structural decisions retain a separate trust role.

Hashes bind recorded bytes, not execution authenticity. Native translations are
still trusted. Completed-trial medians/ranges are descriptive; an incomplete
sequence cannot satisfy the primary three-of-three criterion. No v1 trial can
substitute for any v2 trial. No producer or external native tool is invoked here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.completion_v1.verify_qualification import (
    OBLIGATIONS, decode_json, digest, finite_seconds, relative, require,
    check_sat_assignment, native_commands,
)
from research.completion_v1.verify_study import (
    FILE_LIMIT, audit_unarchived, check_stream, file_inventory, stage_journal,
    summaries, trial_reader, study_directory as archived_study_directory,
    validate_protocol as validate_prior_protocol,
)
from research.proof_interface_v1.lrat import check_lrat_text

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_STUDY = HERE / "study_20260927_v2"
SCHEMA = "alc-completion-study-evidence-v2"


def study_directory(base=DEFAULT_STUDY):
    return archived_study_directory(base)


def write_manifest(base):
    """Seal only after execution, without replacing any earlier seal."""
    base = Path(base)
    record = {"schema": SCHEMA, "files": file_inventory(base)}
    with (base / "MANIFEST.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    return record


def validate_protocol(record):
    """Bind both generations, but require only the new observations below."""
    from research.completion_v2.study import (
        SOURCES, KIND, PRIOR_FREEZE, PRIOR_ARCHIVE, RESTART_POLICY,
        case_records, trial_order,
    )
    require(record["schema"] == 2 and record["kind"] == KIND, "Unknown amended study freeze")
    require(record["cases"] == case_records() and record["order"] == trial_order(),
            "Fixed cases/order changed")
    require(set(record["source_files_sha256"]) == set(SOURCES), "Incomplete amended source freeze")
    for name, expected in record["source_files_sha256"].items():
        require(digest((ROOT / relative(name)).read_bytes()) == expected, "Frozen source changed: " + name)
    prior_raw = (ROOT / PRIOR_FREEZE).read_bytes()
    prior = decode_json(prior_raw)
    validate_prior_protocol(prior)
    require(record["prior_protocol_freeze"] == {"path": PRIOR_FREEZE, "sha256": digest(prior_raw)},
            "Prior freeze binding changed")
    require(record["prior_study_archive_manifest"] == {
        "path": PRIOR_ARCHIVE, "sha256": digest((ROOT / PRIOR_ARCHIVE).read_bytes())},
        "Prior suspended archive binding changed")
    require(record["restart_policy"] == RESTART_POLICY, "Fresh complete-run requirement changed")
    qualification_raw = (HERE / "qualification/MANIFEST.json").read_bytes()
    require(digest(qualification_raw) == record["qualification_manifest_sha256"], "Amended qualification changed")
    require(decode_json(qualification_raw)["binary_sha256"] == record["binary_sha256"] == prior["binary_sha256"],
            "Executables differ from the original or amended qualification")
    require(record["environment_overrides"] == prior["environment_overrides"] and record["seed"] == 0,
            "Frozen environment changed")
    require(record["limits"] == dict(prior["limits"], metadata_bytes=FILE_LIMIT),
            "Amendment changed a resource limit beyond metadata accounting")


def is_raw(name):
    # This is an independent description of the finite prospective allowlist.
    # No suffix rule exempts arbitrary JSON/log files or temporary directories.
    return name not in metadata_paths()


def metadata_paths():
    names = {"workflow.stdout", "workflow.stderr"}
    for name in ("JOURNAL.json", "RESULT.json", "CONSTRUCTION.json"):
        names.add("data/" + name)
        names.add("data/" + name + ".tmp")
    names.add("data/STAGES.jsonl")
    stages = ["ric3", "generate", "split"] + [n + suffix for n in OBLIGATIONS for suffix in ("_cnf", "_solve", "_replay")]
    names.update("data/" + stage + "." + stream + ".txt" for stage in stages for stream in ("stdout", "stderr"))
    return names


def validate_trial(row, case, freeze, inventory, read):
    """Validate evidence and derive status; never trust a supplied summary."""
    supervisor = decode_json(read("SUPERVISOR.json"))
    require(supervisor["schema"] == "alc-bounded-workflow-v2" and
            supervisor["limits"] == freeze["limits"] and supervisor["cpu"] == freeze["limits"]["cpu"],
            "Changed supervisor resource policy")
    require(supervisor["instantaneous_aggregate_quota"] is False, "False aggregate quota claim")
    require(supervisor["artifact_policy"] == "independent sampled raw-artifact and metadata acceptance caps",
            "Changed storage accounting policy")
    artifact_root = Path(supervisor["artifact_root"])
    require(artifact_root.name == row["id"], "Changed trial artifact directory")
    command = supervisor["command"]
    require(command[:3] == [freeze["python"]["executable"], "-m", "research.completion_v1.worker"]
            and (len(command) - 3) % 2 == 0, "Changed worker command")
    options = dict(zip(command[3::2], command[4::2]))
    require(len(options) * 2 + 3 == len(command), "Duplicate worker option")
    expected = {"--route": row["route"], "--model": str(Path(supervisor["cwd"]) / case["model"]),
                "--output": str(artifact_root / "data"), "--tools": options.get("--tools")}
    if row["route"] in ("exporter", "structural"):
        expected.update({"--width": str(case["width"]), "--taps": hex(case["taps"])})
    if row["route"] == "exporter":
        expected["--odd-multiple"] = str(case["odd_multiple"])
    require(options == expected and isinstance(options["--tools"], str), "Changed source-bound worker command")
    total = finite_seconds(supervisor["wall_seconds"], "supervisor total")
    for key in ("cleanup_seconds", "cpu_user_seconds", "cpu_system_seconds", "child_cpu_user_seconds",
                "child_cpu_system_seconds", "max_poll_gap_seconds"):
        finite_seconds(supervisor[key], key)
    all_bytes = sum(v["raw_bytes"] for k, v in inventory.items() if k != "SUPERVISOR.json")
    raw_bytes = sum(v["raw_bytes"] for k, v in inventory.items() if k != "SUPERVISOR.json" and is_raw(k))
    metadata_bytes = all_bytes - raw_bytes
    require(supervisor["all_trial_files_bytes"] == supervisor["artifact_final_bytes"] == all_bytes and
            supervisor["raw_artifact_bytes"] == raw_bytes and supervisor["metadata_bytes"] == metadata_bytes,
            "Retained bytes differ from measured final storage")
    for key in ("artifact_peak_observed_bytes", "open_deleted_peak_observed_bytes",
                "raw_artifact_peak_observed_bytes", "metadata_peak_observed_bytes"):
        require(type(supervisor[key]) is int and supervisor[key] >= 0, "Invalid observed storage peak")
    require(raw_bytes <= supervisor["raw_artifact_peak_observed_bytes"] <= supervisor["artifact_peak_observed_bytes"]
            and metadata_bytes <= supervisor["metadata_peak_observed_bytes"] <= supervisor["artifact_peak_observed_bytes"]
            and all_bytes <= supervisor["artifact_peak_observed_bytes"] <=
            supervisor["raw_artifact_peak_observed_bytes"] + supervisor["metadata_peak_observed_bytes"]
            and supervisor["open_deleted_peak_observed_bytes"] <= supervisor["raw_artifact_peak_observed_bytes"],
            "Inconsistent observed storage peaks")
    for stream in ("stdout", "stderr"):
        check_stream(supervisor, stream, read("workflow." + stream), 1 << 20, bound_text=True)

    result = decode_json(read("data/RESULT.json")) if "data/RESULT.json" in inventory else None
    record = decode_json(read("data/JOURNAL.json")) if "data/JOURNAL.json" in inventory else None
    if result is not None:
        require(result == record and "active_phase" not in result and result.get("finished_utc"),
                "Completed worker result/journal disagree")
        output_raw = read("workflow.stdout")
        expected_output = {"status": result["status"], "reason": result.get("reason")}
        # RESULT is written immediately before stdout. A deadline in between
        # must not turn missing/partial stdout into a counterfeit completion.
        if supervisor["status"] == "completed":
            require(decode_json(output_raw) == expected_output, "Worker output/result disagree")
        else:
            require((json.dumps(expected_output) + "\n").encode().startswith(output_raw),
                    "Stopped worker output/result disagree")
    expected_status = "structural_accepted" if row["route"] == "structural" else "accepted"
    conflicts = []
    metadata_excess = (supervisor["metadata_peak_observed_bytes"] > freeze["limits"]["metadata_bytes"] or
                       supervisor.get("reason") == "metadata_limit" or
                       "metadata_limit" in supervisor["observed_violations"])
    if metadata_excess:
        conflicts.append("metadata budget exceeded; not an eligible coverage loss")
    if supervisor["cleanup"]["complete"] is not True or supervisor["cleanup"].get("remaining_pids"):
        conflicts.append("incomplete descendant cleanup")
    phases, obligations = [], []
    if record is not None:
        require(record["schema"] == 1 and record["route"] == row["route"] and
                record["model_source"] == options["--model"], "Changed worker source/route")
        require(record["output_contract"] == ("source-aware structural decision" if row["route"] == "structural"
                else "source-bound Certifaiger witness with nine LRAT checks"), "Changed output contract")
        worker_total = finite_seconds(record["worker_wall_seconds"], "worker total")
        require(worker_total <= total + 1e-6, "Worker time exceeds supervisor total")
        if row["route"] in ("exporter", "structural"):
            hints = {"width": case["width"], "taps": case["taps"]}
            if row["route"] == "exporter":
                hints["odd_multiple"] = case["odd_multiple"]
            require(record["hints"] == hints, "Changed structural hints")
        if "model_sha256" in record:
            model = read("data/model.aag")
            require(digest(model) == case["sha256"] == record["model_sha256"] and
                    len(model) == record["model_bytes"], "Changed original source bytes")
        if "witness_sha256" in record:
            witness = read("data/witness.aag")
            require(digest(witness) == record["witness_sha256"] and len(witness) == record["witness_bytes"],
                    "Changed witness bytes")
        if "construction" in record:
            require(record["construction"] == decode_json(read("data/CONSTRUCTION.json")),
                    "Construction metadata differs")
        if record["status"] not in ("incomplete", expected_status):
            file_excess = (record["status"] == "unknown" and record.get("resource_cause") == "file_size_limit"
                           and supervisor.get("reason") == "artifact_limit")
            if not file_excess:
                conflicts.append("worker " + record["status"])
        phases, obligations = record["phases"], record["obligations"]

    native, _ = native_commands(None)
    if row["route"] == "structural":
        sequence, native = ["preflight", "read_original", "structural_decision"], []
    else:
        sequence = ["preflight", "read_original", "construct" if row["route"] == "exporter" else "ric3",
                    "witness_metadata"] + [entry[0] for entry in native]
        if row["route"] == "ric3":
            native.insert(0, ("ric3", "ric3", ["check", "model.aag", "--cert", "witness.aag", "--ui", "false",
                                             "ic3", "--rseed", "0"], 0))
    require([p["name"] for p in phases] == sequence[:len(phases)], "Missing/reordered workflow phase")
    require(len(phases) <= len(sequence), "Extra workflow phase")
    require([o["name"] for o in obligations] == list(OBLIGATIONS[:len(obligations)])
            and len(obligations) <= len(OBLIGATIONS), "Changed obligation order")
    if row["route"] == "structural":
        require(not obligations and "data/witness.aag" not in inventory, "Structural reference masquerades as witness")
    native_map = {name: (tool, tail, code) for name, tool, tail, code in native}
    previous_end = 0.0
    for index, phase in enumerate(phases):
        require(phase["status"] in ("running", "completed", "failed"), "Unknown phase status")
        start = finite_seconds(phase["start_offset_seconds"], "phase start")
        require(start >= previous_end - 1e-6, "Overlapping/out-of-order phases")
        if phase["status"] == "running":
            require(index == len(phases) - 1 and result is None, "Nonterminal active phase")
        else:
            previous_end = start + finite_seconds(phase["wall_seconds"], "phase wall")
            require(previous_end <= record["worker_wall_seconds"] + 1e-6, "Phase exceeds worker time")
            for key in ("cpu_user_seconds", "cpu_system_seconds"):
                finite_seconds(phase[key], key)
            if phase["status"] == "failed" and "process" not in phase:
                conflicts.append("failed worker phase")
        if phase["name"] in native_map:
            tool, tail, _ = native_map[phase["name"]]
            require(phase["argv"] == [str(Path(options["--tools"]) / tool)] + tail, "Changed native command")
        else:
            require("argv" not in phase and "process" not in phase, "Unexpected native phase")

    journal = stage_journal(read("data/STAGES.jsonl")) if "data/STAGES.jsonl" in inventory else []
    finishes, active = {}, None
    started = 0
    for entry in journal:
        require(started <= len(native), "Unexpected native stage")
        if entry["event"] == "start":
            require(active is None and started < len(native), "Overlapping/extra native stage")
            name, tool, tail, code = native[started]
            require(entry["command"] == [str(Path(options["--tools"]) / tool)] + tail and
                    entry["cwd"] == options["--output"], "Changed native journal command/context")
            active = (name, code, entry)
            started += 1
        else:
            require(entry["event"] == "finish" and active is not None, "Native finish without start")
            name, code, start_entry = active
            require(all(entry[k] == start_entry[k] for k in ("command", "cwd", "started_utc")),
                    "Native start/finish disagree")
            for key in ("wall_seconds", "cpu_user_seconds", "cpu_system_seconds"):
                finite_seconds(entry[key], key)
            for stream in ("stdout", "stderr"):
                check_stream(entry, stream, read("data/" + name + "." + stream + ".txt"), 1 << 20, bound_text=True)
                require(entry[stream + "_path"] == str(Path(options["--output"]) / (name + "." + stream + ".txt")),
                        "Changed native stream path")
                if entry[stream + "_truncated"]:
                    conflicts.append("native output truncation")
            file_excess = (entry["status"] == "completed" and entry.get("resource_signal") == "file_size_limit"
                           and supervisor.get("reason") == "artifact_limit")
            if not file_excess and (entry["status"] != "completed" or entry["exit_code"] != code):
                conflicts.append("native failure: " + name)
            if entry.get("resource_signal") and not file_excess:
                conflicts.append("unattributed native resource signal: " + name)
            finishes[name] = entry
            active = None
    for phase in phases:
        if "process" in phase:
            require(phase["name"] in finishes, "Process observation lacks native journal finish")
            finish = finishes[phase["name"]]
            require(phase["process"] == {k: v for k, v in finish.items() if k not in ("event", "stdout", "stderr")},
                    "Native phase/journal disagree")

    proofs, sat = [], []
    for name in OBLIGATIONS:
        log_name = "data/" + name + "_solve.stdout.txt"
        if log_name in inventory and b"s SATISFIABLE" in read(log_name).splitlines():
            conflicts.append("retained SAT verdict: " + name)
        solve = finishes.get(name + "_solve")
        if solve and solve["status"] == "completed" and solve["exit_code"] in (10, 20):
            cnf = read("data/" + name + ".cnf")
            if solve["exit_code"] == 10:
                sat.append({"name": name, **check_sat_assignment(cnf, read(log_name))})
            else:
                checked = check_lrat_text(cnf.decode("ascii"), read("data/" + name + ".lrat").decode("ascii"))
                require(checked["status"] == "verified_unsat", "Independent proof replay failed")
                proofs.append(name)
    for obligation in obligations:
        require(obligation["status"] in ("incomplete", "sat", "unsat_replayed"), "Unknown obligation status")
        if obligation["status"] == "unsat_replayed":
            finish = finishes.get(obligation["name"] + "_replay", {})
            require(obligation["name"] in proofs and finish.get("status") == "completed" and finish.get("exit_code") == 20,
                    "Claimed native replay lacks evidence")
        if obligation["status"] == "sat":
            require(obligation["name"] in [v["name"] for v in sat], "Claimed SAT lacks checked assignment")
            conflicts.append("SAT obligation")
    if "data/ric3.stdout.txt" in inventory:
        verdicts = [line.strip() for line in read("data/ric3.stdout.txt").decode(errors="replace").splitlines()
                    if line.strip() in ("UNSAT", "SAT", "UNKNOWN")]
        if verdicts and verdicts != ["UNSAT"]:
            conflicts.append("retained rIC3 verdict conflict")
        if "ric3" in finishes and finishes["ric3"].get("exit_code") == 0:
            require(verdicts == ["UNSAT"] or conflicts, "Missing rIC3 verdict")

    violations = supervisor["observed_violations"]
    require(isinstance(violations, list) and len(violations) == len(set(violations)), "Invalid resource violations")
    accepted = (supervisor["status"] == "completed" and supervisor["reason"] is None and
                supervisor["exit_code"] == 0 and not violations and not conflicts and result is not None and
                result["status"] == expected_status)
    if accepted:
        require(total <= 30 and supervisor["raw_artifact_peak_observed_bytes"] <= FILE_LIMIT and
                supervisor["metadata_peak_observed_bytes"] <= freeze["limits"]["metadata_bytes"] and
                supervisor["artifact_peak_observed_bytes"] <= FILE_LIMIT + freeze["limits"]["metadata_bytes"] and
                not supervisor["stdout_truncated"] and not supervisor["stderr_truncated"], "Accepted trial exceeded limits")
        require(len(phases) == len(sequence) and all(p["status"] == "completed" for p in phases),
                "Accepted trial omitted a workflow phase")
        require(record.get("model_sha256") == case["sha256"], "Accepted trial lacks source binding")
        if row["route"] != "structural":
            require(record.get("witness_sha256") is not None and len(proofs) == 9 and
                    len(obligations) == 9 and all(o["status"] == "unsat_replayed" for o in obligations),
                    "Accepted witness lacks all nine checked obligations")
            require(len(finishes) == len(native) and active is None, "Accepted witness has incomplete commands")
            require(all("process" in p for p in phases if p["name"] in native_map),
                    "Accepted native phase lacks process observations")
            for filename in ("check.aig",) + tuple(n + ".aig" for n in OBLIGATIONS):
                read("data/" + filename)
    limited = (supervisor["status"] == "resource_limit" and supervisor["reason"] in ("deadline", "artifact_limit")
               and supervisor["reason"] in violations and set(violations) <= {"deadline", "artifact_limit"} and not conflicts)
    if limited:
        if "deadline" in violations:
            require(total >= 30, "Deadline label lacks elapsed deadline")
        if "artifact_limit" in violations:
            require(supervisor["raw_artifact_peak_observed_bytes"] > FILE_LIMIT, "Raw limit lacks observed excess")
    status = expected_status if accepted else "resource_unknown" if limited else "execution_issue"
    if status == "execution_issue" and supervisor["status"] != "completed":
        conflicts.append("ineligible supervisor outcome: " + supervisor["status"] + "/" + str(supervisor["reason"]))
    return {**row, "status": status, "worker_status": result["status"] if result else None,
            "supervisor_status": supervisor["status"], "supervisor_reason": supervisor["reason"],
            "resource_reason": supervisor["reason"] if limited else None, "conflicts": sorted(set(conflicts)),
            "wall_seconds": total, "raw_artifact_bytes": raw_bytes, "all_trial_files_bytes": all_bytes,
            "metadata_bytes": metadata_bytes,
            "proofs_replayed": proofs, "sat_assignments_checked": sat}



def _verify_study_directory(base):
    base = Path(base)
    manifest = decode_json((base / "MANIFEST.json").read_bytes())
    require(manifest["schema"] == SCHEMA and manifest["files"] == file_inventory(base), "Study inventory changed")
    frozen = (HERE / "PROTOCOL_FREEZE.json").read_bytes()
    require((base / "PROTOCOL_COPY.json").read_bytes() == frozen, "Study differs from prospective freeze")
    freeze = decode_json(frozen)
    validate_protocol(freeze)
    planned = freeze["order"]
    actual = {p.name for p in base.iterdir() if p.is_dir()}
    require(actual == {r["id"] for r in planned[:len(actual)]}, "Study trials are not an exact planned prefix")
    topfiles = {p.name for p in base.iterdir() if p.is_file()}
    require(topfiles <= {"MANIFEST.json", "PROTOCOL_COPY.json", "SUSPENDED.json"}, "Unrecognized study control file")
    suspension = decode_json((base / "SUSPENDED.json").read_bytes()) if "SUSPENDED.json" in topfiles else None
    if suspension is not None:
        require(actual and suspension["trial"] == planned[len(actual)-1]["id"], "Suspension is not at the last trial")
    else:
        require(len(actual) == len(planned), "Incomplete study lacks suspension record")
    cases = {c["width"]: c for c in freeze["cases"]}
    rows = []
    for index, row in enumerate(planned[:len(actual)]):
        directory = base / row["id"]
        if not (directory / "ARTIFACTS.json").is_file():
            require(suspension is not None and index == len(actual)-1 and
                    suspension["reason"] == "Supervisor infrastructure failure", "Unarchived nonsuspended trial")
            proofs, sat = audit_unarchived(directory)
            rows.append({**row, "status": "execution_issue", "worker_status": None,
                         "supervisor_status": None, "supervisor_reason": "infrastructure failure",
                         "resource_reason": None, "conflicts": ["supervisor infrastructure failure"],
                         "wall_seconds": None, "raw_artifact_bytes": None, "all_trial_files_bytes": None,
                         "metadata_bytes": None,
                         "proofs_replayed": proofs, "sat_assignments_checked": sat})
            continue
        inventory, read = trial_reader(directory)
        checked = validate_trial(row, cases[row["width"]], freeze, inventory, read)
        require(checked["status"] != "execution_issue" or suspension is not None and index == len(actual)-1,
                "Execution issue did not suspend the study")
        rows.append(checked)
    if suspension is not None:
        require(rows[-1]["status"] == "execution_issue", "Suspension lacks an execution issue")
    complete = suspension is None and len(rows) == len(planned)
    return {"schema": SCHEMA, "status": "complete" if complete else "suspended",
            "planned_trials": len(planned), "observed_trials": len(rows), "trials": rows,
            "proofs_replayed": sum(len(r["proofs_replayed"]) for r in rows),
            "sat_assignments_checked": sum(len(r["sat_assignments_checked"]) for r in rows),
            **summaries(rows, freeze, complete),
            "boundary": "Independent CNF proof replay; native translations remain trusted; structural decisions are separate"}


def verify_study(base=DEFAULT_STUDY):
    with study_directory(base) as directory:
        return _verify_study_directory(directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, default=DEFAULT_STUDY)
    parser.add_argument("--seal", action="store_true", help="Write a new post-run manifest, without replacing one")
    args = parser.parse_args()
    if args.seal:
        write_manifest(args.study)
    print(json.dumps(verify_study(args.study), indent=2))


if __name__ == "__main__":
    main()
