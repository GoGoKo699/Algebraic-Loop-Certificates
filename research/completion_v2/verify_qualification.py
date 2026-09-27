"""Offline qualification for the prospective, independently budgeted v2 harness.

The four synthetic controls and all native executable identities are unchanged.
The frozen v1 artifact, proof and build validators are reused; the case validator
is versioned here so no historical observation is rewritten or projected into a
new schema. Proof replay certifies CNF unsatisfiability only: native translations
remain trusted.
"""
from __future__ import annotations

import json
from pathlib import Path

from research.proof_interface_v1.lrat import check_lrat_text
from research.completion_v2.resources import _is_raw
from research.completion_v1.verify_qualification import (
    CASES, LIMIT, MODEL, MODEL_SHA256, OBLIGATIONS, ROOT,
    artifact_reader, check_sat_assignment, decode_json, digest, finite_seconds,
    native_commands, reconstruct_ric3_mutation, relative, require,
    validate_provenance as _validate_native_provenance,
)

HERE = Path(__file__).resolve().parent
QUALIFICATION = HERE / "qualification"
PRIOR_QUALIFICATION = ROOT / "research/completion_v1/qualification"
PRIOR_MANIFEST_SHA256 = "9c7cfd666a9ffd29d41bb72a82f488f6be483592c01953589be7f3d33e0a6be6"
REQUIRED_SOURCES = frozenset({
    "research/completion_v2/resources.py",
    "research/completion_v2/verify_qualification.py",
    "research/completion_v1/worker.py",
    "research/completion_v1/resources.py",
    "research/completion_v1/verify_qualification.py",
    "research/odd_order_witness_v1/produce.py",
    "research/proof_interface_v1/produce.py",
    "research/aiger_lfsr_v1/check.py",
    "research/aiger_lfsr_v1/source_aware.py",
    "research/proof_interface_v1/lrat.py",
})


def validate_case(case, record, supervisor, read):
    """Validate one loaded observation and replay its proof prefix.

    ``read`` must return already bound raw artifact bytes by logical name. Keeping
    this boundary explicit permits tests to exercise corrupted records/proofs
    instead of merely checking that a changed file has a different hash.
    """
    label = case["id"]
    require(label in CASES, "Unknown compatibility case")
    route = {"exporter": "exporter", "ric3": "ric3", "exporter_bad": "exporter",
             "ric3_bad": "witness-control"}[label]
    expected_status = "rejected" if label.endswith("_bad") else "accepted"
    rejected = case["expected_rejected_obligation"]
    require(case["route"] == route and case["expected_status"] == expected_status,
            "Changed qualification route or expected verdict")
    if label == "exporter_bad":
        require(case["mutation"] == {"kind": "global_bound"} and rejected == "Inductive",
                "Changed exporter negative control")
    elif label == "ric3_bad":
        require(case["mutation"] == {"kind": "mapped_reset_flip", "latch_index": 0,
                                     "before": "0", "after": "1"} and rejected == "Reset",
                "Changed rIC3 reset corruption")
    else:
        require(case["mutation"] is None and rejected is None, "Changed positive control")
    prefix = label + "/data/"
    require(case["worker_result"] == prefix + "RESULT.json" and
            case["supervisor_result"] == label + "/SUPERVISOR.json", "Changed record locations")
    require(record["schema"] == 1 and record["route"] == route and record["status"] == expected_status,
            "Worker verdict does not match fixed qualification control")
    require("active_phase" not in record and record.get("finished_utc"), "Worker record is incomplete")
    require(record["output_contract"] == "source-bound Certifaiger witness with nine LRAT checks",
            "Changed witness acceptance contract")
    require(decode_json(read(prefix + "JOURNAL.json")) == record, "Journal/result records disagree")
    raw, witness = read(prefix + "model.aag"), read(prefix + "witness.aag")
    require(digest(raw) == MODEL_SHA256 == case["model_sha256"] == record["model_sha256"],
            "Original model binding changed")
    require(record["model_bytes"] == len(raw) and record["witness_bytes"] == len(witness) and
            digest(witness) == case["witness_sha256"] == record["witness_sha256"],
            "Consumed source/witness bytes changed")
    if label.startswith("exporter"):
        # This is a reproducibility check on untrusted producer output. The
        # independent CNF proof checker below imports no producer or solver.
        from research.odd_order_witness_v1.produce import produce
        regenerated, metadata = produce(raw, 4, 9, mutation="global_bound" if label.endswith("_bad") else None)
        require(regenerated == witness, "Exporter witness differs from fixed construction")
        require(metadata == record["construction"] == decode_json(read(prefix + "CONSTRUCTION.json")),
                "Construction metadata changed")
    if label == "ric3_bad":
        original = read("ric3/data/witness.aag")
        require(decode_json(read("controls/MUTATION.json")) == case["mutation"],
                "Corruption record differs from qualification manifest")
        require(reconstruct_ric3_mutation(original, case["mutation"]) == witness,
                "rIC3 control is not the specified single-line corruption")

    require(supervisor["schema"] == "alc-bounded-workflow-v2" and
            supervisor["status"] == "completed" and supervisor["reason"] is None and
            type(supervisor["exit_code"]) is int and supervisor["exit_code"] == 0,
            "Completed smoke contains a supervisor failure or limit exhaustion")
    require(supervisor["cleanup"]["complete"] is True and
            not supervisor["cleanup"].get("remaining_pids"), "Descendant cleanup failed")
    require(supervisor["observed_violations"] == [], "Completed smoke contains a recorded violation")
    command = supervisor["command"]
    require(isinstance(command, list) and len(command) >= 3 and
            command[1:3] == ["-m", "research.completion_v1.worker"] and (len(command) - 3) % 2 == 0,
            "Supervisor did not invoke the fixed worker")
    pairs = list(zip(command[3::2], command[4::2]))
    options = dict(pairs)
    require(len(options) == len(pairs), "Duplicate worker command option")
    expected_options = {"--route", "--model", "--tools", "--output"}
    if route == "exporter":
        expected_options |= {"--width", "--taps", "--odd-multiple"}
        require(options.get("--width") == "3" and options.get("--taps") == "0x4" and
                options.get("--odd-multiple") == "9", "Changed exporter smoke hints")
        if label == "exporter_bad":
            expected_options.add("--mutation")
            require(options.get("--mutation") == "global_bound", "Changed exporter mutation command")
    elif route == "witness-control":
        expected_options.add("--witness")
        require(options.get("--witness") == record["control_witness_source"], "Control source command changed")
        require(read("controls/" + Path(options["--witness"]).name) == witness,
                "Consumed control differs from retained corrupted witness")
    require(set(options) == expected_options and options["--route"] == route and
            options["--model"] == record["model_source"] and
            Path(options["--model"]).as_posix().endswith("/" + MODEL) and
            Path(options["--output"]).as_posix().endswith("/" + label + "/data"),
            "Worker command differs from the fixed source-bound route")
    limits = supervisor["limits"]
    require(limits["wall_seconds"] == 30 and limits["address_space_bytes"] == 1 << 30 and
            limits["artifact_bytes"] == LIMIT and limits["metadata_bytes"] == LIMIT and
            limits["output_bytes"] == 1 << 20 and
            limits["poll_seconds"] == 0.01, "Qualification resource limits changed")
    require(supervisor["instantaneous_aggregate_quota"] is False, "False aggregate quota claim")
    require(type(supervisor["cpu"]) is int and supervisor["cpu"] >= 0 and
            limits["cpu"] in (None, supervisor["cpu"]), "Invalid CPU affinity record")
    total = finite_seconds(supervisor["wall_seconds"], "supervisor total")
    require(total <= limits["wall_seconds"], "Completed smoke exceeded total deadline")
    worker_total = finite_seconds(record["worker_wall_seconds"], "worker total")
    require(worker_total <= total, "Worker time exceeds enclosing workflow")
    for key in ("cleanup_seconds", "cpu_user_seconds", "cpu_system_seconds", "child_cpu_user_seconds",
                "child_cpu_system_seconds", "max_poll_gap_seconds"):
        finite_seconds(supervisor[key], key)
    for key in ("raw_artifact_bytes", "raw_artifact_peak_observed_bytes",
                "metadata_bytes", "metadata_peak_observed_bytes", "open_deleted_peak_observed_bytes"):
        require(type(supervisor[key]) is int and 0 <= supervisor[key] <= LIMIT,
                "Completed smoke has an invalid or exceeded component storage observation")
    for key in ("artifact_peak_observed_bytes", "artifact_final_bytes", "all_trial_files_bytes"):
        require(type(supervisor[key]) is int and 0 <= supervisor[key] <= 2 * LIMIT,
                "Completed smoke has an invalid total storage observation")
    require(supervisor["artifact_peak_observed_bytes"] >= supervisor["artifact_final_bytes"],
            "Storage peak is below the final observation")
    require(supervisor["artifact_final_bytes"] == supervisor["all_trial_files_bytes"] ==
            supervisor["raw_artifact_bytes"] + supervisor["metadata_bytes"],
            "Independent final storage components do not sum to all files")
    raw_peak = supervisor["raw_artifact_peak_observed_bytes"]
    metadata_peak = supervisor["metadata_peak_observed_bytes"]
    require(supervisor["raw_artifact_bytes"] <= raw_peak <= supervisor["artifact_peak_observed_bytes"] and
            supervisor["metadata_bytes"] <= metadata_peak <= supervisor["artifact_peak_observed_bytes"] and
            supervisor["artifact_peak_observed_bytes"] <= raw_peak + metadata_peak and
            supervisor["open_deleted_peak_observed_bytes"] <= raw_peak,
            "Independent storage peaks or deleted-raw observations disagree")
    for stream in ("stdout", "stderr"):
        content = read(label + "/workflow." + stream)
        require(supervisor[stream + "_truncated"] is False and
                supervisor[stream + "_bytes"] == len(content) <= 1 << 20 and
                supervisor[stream] == content.decode("utf-8", errors="replace"),
                "Workflow stream is truncated or unbound")
    output = decode_json(read(label + "/workflow.stdout"))
    require(output["status"] == expected_status and output.get("reason") == record.get("reason"),
            "Worker stdout/result disagree")

    native, names = native_commands(rejected)
    initial = ["preflight", "read_original", {"exporter": "construct", "ric3": "ric3",
                                               "witness-control": "copy_control"}[route], "witness_metadata"]
    phases = record["phases"]
    require([row["name"] for row in phases] == initial + [row[0] for row in native],
            "Missing, duplicated or reordered workflow phase")
    require(tuple(row["name"] for row in record["obligations"]) == names,
            "Missing, duplicated or reordered obligation")
    stage_rows = []
    phase_total = 0.0
    previous_end = 0.0
    for row in phases:
        require(row["status"] == "completed" and "exception" not in row, "Incomplete workflow phase")
        wall = finite_seconds(row["wall_seconds"], row["name"])
        start = finite_seconds(row["start_offset_seconds"], row["name"] + " start")
        require(start >= previous_end - 1e-6, "Workflow phases overlap or run out of order")
        previous_end = start + wall
        phase_total += wall
        for key in ("cpu_user_seconds", "cpu_system_seconds"):
            finite_seconds(row[key], row["name"] + " " + key)
        if "argv" in row:
            process = row["process"]
            require(process["command"] == row["argv"] and process["status"] == "completed",
                    "Native command process is incomplete or changed")
            require(process["cwd"] == options["--output"] and not process.get("resource_signal"),
                    "Native stage escaped its working directory or hit a resource limit")
            require(type(process["exit_code"]) is int, "Native exit code is missing")
            for key in ("wall_seconds", "cpu_user_seconds", "cpu_system_seconds"):
                finite_seconds(process[key], row["name"] + " process " + key)
            for stream in ("stdout", "stderr"):
                content = read(prefix + row["name"] + "." + stream + ".txt")
                require(process[stream + "_truncated"] is False and
                        process[stream + "_bytes"] == len(content) <= 1 << 20,
                        "Native stream is truncated or unbound")
                require(Path(process[stream + "_path"]).name == row["name"] + "." + stream + ".txt",
                        "Native stream path changed")
            stage_rows.append(row)
    require(phase_total <= worker_total + 1e-6 and previous_end <= worker_total + 1e-6,
            "Phase times exceed worker total")
    expected_commands = list(native)
    if route == "ric3":
        expected_commands.insert(0, ("ric3", "ric3", ["check", "model.aag", "--cert", "witness.aag",
                                                       "--ui", "false", "ic3", "--rseed", "0"], 0))
    require(len(stage_rows) == len(expected_commands), "Unexpected command-bearing stage")
    for row, (name, tool, tail, code) in zip(stage_rows, expected_commands):
        require(row["name"] == name and row["argv"][0] == str(Path(options["--tools"]) / tool) and
                row["argv"][1:] == tail,
                "Native command changed")
        require(row["process"]["exit_code"] == code, "Native exit code does not establish its obligation")
    if route == "ric3":
        verdicts = [line.strip() for line in read(prefix + "ric3.stdout.txt").decode("utf-8").splitlines()
                    if line.strip() in ("UNSAT", "SAT", "UNKNOWN")]
        require(verdicts == ["UNSAT"], "rIC3 did not report an unambiguous safe result")
    journal = [decode_json(line) for line in read(prefix + "STAGES.jsonl").splitlines()]
    require(len(journal) == 2 * len(stage_rows), "Native command journal is incomplete")
    for row, start, finish in zip(stage_rows, journal[::2], journal[1::2]):
        require(start["event"] == "start" and finish["event"] == "finish" and
                start["command"] == finish["command"] == row["argv"], "Stage journal command changed")
        require(start["cwd"] == finish["cwd"] and start["started_utc"] == finish["started_utc"],
                "Stage journal start/finish context changed")
        require({key: value for key, value in finish.items() if key not in ("event", "stdout", "stderr")}
                == row["process"], "Stage journal/result observations disagree")
        for stream in ("stdout", "stderr"):
            require(finish[stream] == read(prefix + row["name"] + "." + stream + ".txt").decode("utf-8", errors="replace"),
                    "Stage journal stream changed")
    for filename in ("check.aig",) + tuple(name + ".aig" for name in OBLIGATIONS):
        read(prefix + filename)
    count = 0
    negative = None
    for obligation in record["obligations"]:
        name = obligation["name"]
        cnf = read(prefix + name + ".cnf")
        if name == rejected:
            require(obligation["status"] == "sat" and record.get("reason") == "SAT counterexample to " + name,
                    "Negative witness was not rejected by the designated obligation")
            negative = check_sat_assignment(cnf, read(prefix + name + "_solve.stdout.txt"))
        else:
            require(obligation["status"] == "unsat_replayed", "Completed proof was not replayed")
            checked = check_lrat_text(cnf.decode("ascii"), read(prefix + name + ".lrat").decode("ascii"))
            require(checked["status"] == "verified_unsat", "Independent LRAT replay failed")
            count += 1
    return {"case": label, "status": expected_status, "proofs_replayed": count,
            "rejected_obligation": rejected, "sat_assignment": negative}



def validate_provenance(manifest, read):
    """Retain the previous qualification's exact tools and pristine build dossier."""
    prior_raw = (PRIOR_QUALIFICATION / "MANIFEST.json").read_bytes()
    require(manifest["prior_qualification_manifest_sha256"] == PRIOR_MANIFEST_SHA256 == digest(prior_raw),
            "Previous qualification manifest binding changed")
    prior = decode_json(prior_raw)
    require(manifest["binary_sha256"] == prior["binary_sha256"],
            "Native binary identities differ from the previous qualified tools")
    require(all(manifest["source_files_sha256"].get(name) == expected
                for name, expected in prior["source_files_sha256"].items()),
            "Previously qualified worker or helper source binding changed")
    _validate_native_provenance(manifest, read)
    build_names = {name for name in prior["artifacts"] if name.startswith("build/")}
    require(build_names == {name for name in manifest["artifacts"] if name.startswith("build/")},
            "Previous build dossier inventory changed")
    for name in build_names:
        item = prior["artifacts"][name]
        raw = read(name)
        require(len(raw) == item["raw_bytes"] and digest(raw) == item["raw_sha256"],
                "Previous build dossier bytes changed: " + name)


def validate_retained_storage(case, supervisor, artifacts):
    """Bind final bytes to the path policy, including unknown/temporary files.

    The supervisor's own report is emitted after measurement. Every other
    retained trial file belongs to exactly one measured component. Open deleted
    files cannot survive final descendant cleanup; their peak remains a separate
    raw-artifact observation checked by ``validate_case``.
    """
    prefix = case["id"] + "/"
    files = {name[len(prefix):]: item for name, item in artifacts.items()
             if name.startswith(prefix) and name != case["supervisor_result"]}
    total = sum(item["raw_bytes"] for item in files.values())
    raw = sum(item["raw_bytes"] for name, item in files.items() if _is_raw(name))
    require(total == supervisor["all_trial_files_bytes"],
            "Retained all-file bytes differ from measured final storage")
    require(raw == supervisor["raw_artifact_bytes"],
            "Retained raw bytes differ from the finite path classification")
    require(total - raw == supervisor["metadata_bytes"],
            "Retained metadata bytes differ from the finite path classification")


def verify_qualification(base=QUALIFICATION):
    base = Path(base)
    manifest = decode_json((base / "MANIFEST.json").read_bytes())
    require(manifest["schema"] == 2 and manifest["model"] == {
        "repository_path": MODEL, "sha256": MODEL_SHA256}, "Qualification manifest/model changed")
    require(digest((ROOT / MODEL).read_bytes()) == MODEL_SHA256, "Original synthetic fixture changed")
    require([case["id"] for case in manifest["cases"]] == list(CASES), "Fixed smoke controls changed")
    require(REQUIRED_SOURCES <= set(manifest["source_files_sha256"]),
            "Missing workflow/checker source binding")
    for name, expected in manifest["source_files_sha256"].items():
        require(digest((ROOT / relative(name)).read_bytes()) == expected, "Frozen source changed: " + name)
    read = artifact_reader(base, manifest["artifacts"])
    validate_provenance(manifest, read)
    rows = []
    for case in manifest["cases"]:
        record = decode_json(read(case["worker_result"]))
        supervisor = decode_json(read(case["supervisor_result"]))
        validate_retained_storage(case, supervisor, manifest["artifacts"])
        rows.append(validate_case(case, record, supervisor, read))
    require(sum(row["status"] == "accepted" for row in rows) == 2 and
            sum(row["status"] == "rejected" for row in rows) == 2, "Incomplete compatibility qualification")
    return {"cases": rows, "proofs_replayed": sum(row["proofs_replayed"] for row in rows),
            "negative_assignments_checked": sum(row["sat_assignment"] is not None for row in rows),
            "checked_artifact_files": len(manifest["artifacts"]),
            "boundary": "CNF proofs and SAT controls checked independently; native translations remain trusted"}


if __name__ == "__main__":
    print(json.dumps(verify_qualification(), indent=2))
