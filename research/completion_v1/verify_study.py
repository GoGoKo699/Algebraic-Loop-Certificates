"""Offline audit of a complete or suspended frozen comparison.

Contract: a post-run manifest binds all retained bytes; the untouched prospective
freeze supplies cases, order, resources and commands. A study is an exact prefix
of its 54 planned trials. An incomplete prefix requires a suspension record and
never establishes the benefit criterion. Completed native UNSAT proofs, including
those preceding a stopped trial, are replayed with the independent CNF checker.
Recorded timings are observations, not proof of runtime reproducibility. Native
translations and the separate structural checker retain their stated trust roles.

Soundness boundary: hashes prevent unnoticed evidence substitution, but are not
signatures or an attestation that tools ran. Checked LRAT establishes only the
supplied CNF's unsatisfiability. Acceptance additionally requires the full recorded
source-bound pipeline and nine native replays. No producer is imported here.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import gzip
import hashlib
import io
import json
from pathlib import Path
from statistics import median
import tarfile
import tempfile

from research.completion_v1.verify_qualification import (
    OBLIGATIONS, decode_json, digest, finite_seconds, relative, require,
    check_sat_assignment, native_commands,
)
from research.proof_interface_v1.lrat import check_lrat_text

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_STUDY = HERE / "study_20260927"
FILE_LIMIT = 64 << 20
SCHEMA = "alc-completion-study-evidence-v1"


def reassemble_archive(parts, target):
    """Losslessly reassemble transport segments; this changes no evidence."""
    require(parts.is_dir() and not parts.is_symlink(), "Missing archive parts directory")
    index_path = parts / "manifest.json"
    require(index_path.is_file() and not index_path.is_symlink() and index_path.stat().st_size <= 1 << 20,
            "Missing/linked/oversized archive parts manifest")
    index = decode_json(index_path.read_bytes())
    require(index["schema"] == "alc-study-archive-parts-v1" and index["archive_name"] == target.name,
            "Unknown segmented study archive")
    entries = index["parts"]
    require(isinstance(entries, list) and 0 < len(entries) <= 256, "Invalid archive part count")
    require([entry["file"] for entry in entries] == [f"part-{i:03d}" for i in range(len(entries))],
            "Missing/reordered archive parts")
    require({p.name for p in parts.iterdir()} == {"manifest.json"} | {p["file"] for p in entries},
            "Unlisted/missing archive part")
    whole, total = hashlib.sha256(), 0
    with target.open("xb") as output:
        for position, entry in enumerate(entries):
            require(type(entry["bytes"]) is int and 0 < entry["bytes"] <= 4 << 20,
                    "Invalid archive part size")
            if position < len(entries)-1:
                require(entry["bytes"] == 4 << 20, "Short nonfinal archive part")
            path = parts / entry["file"]
            require(path.is_file() and not path.is_symlink() and path.stat().st_size == entry["bytes"],
                    "Missing/linked/wrong-size archive part")
            raw = path.read_bytes()
            require(digest(raw) == entry["sha256"], "Archive part hash changed")
            if "git_blob_sha" in entry:
                git_hash = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                require(git_hash == entry["git_blob_sha"], "Archive part Git blob changed")
            whole.update(raw)
            output.write(raw)
            total += len(raw)
            require(total <= 1 << 30, "Reassembled archive exceeds byte bound")
    require(total == index["archive_bytes"] and whole.hexdigest() == index["archive_sha256"],
            "Reassembled archive hash/size changed")


@contextmanager
def study_directory(base=DEFAULT_STUDY):
    """Read a directory or safely unpack its lossless archived distribution.

    No extraction helpers follow archive paths: only ordinary files/directories
    under one expected root are created, with bounded member count and sizes.
    """
    base = Path(base)
    if base.is_dir() and not base.name.endswith(".tar.xz.parts"):
        yield base
        return
    if base.name.endswith(".tar.xz.parts"):
        archive = base.with_name(base.name.removesuffix(".parts"))
    else:
        archive = base if base.name.endswith(".tar.xz") else base.with_name(base.name + ".tar.xz")
    expected_root = archive.name.removesuffix(".tar.xz")
    with tempfile.TemporaryDirectory(prefix="alc-study-evidence-") as temporary:
        root = Path(temporary)
        if not archive.is_file() or base.name.endswith(".tar.xz.parts"):
            parts = archive.with_name(archive.name + ".parts")
            archive = root / archive.name
            reassemble_archive(parts, archive)
        with tarfile.open(archive, "r:xz") as stream:
            seen, total = set(), 0
            for count, member in enumerate(stream, 1):
                require(count <= 10000, "Invalid study archive member count")
                name = str(relative(member.name))
                require(name not in seen and Path(name).parts[0] == expected_root,
                        "Duplicate or misplaced study archive member")
                seen.add(name)
                require(member.isdir() or member.isfile(), "Links/special files in study archive")
                require(type(member.size) is int and 0 <= member.size <= FILE_LIMIT + (1 << 20),
                        "Oversized study archive member")
                total += member.size
                require(total <= 1 << 30, "Study archive exceeds total extraction bound")
                target = root / name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = stream.extractfile(member)
                    require(source is not None, "Unreadable study archive member")
                    with source, target.open("xb") as output:
                        remaining = member.size
                        while remaining:
                            chunk = source.read(min(1 << 20, remaining))
                            require(chunk, "Truncated study archive member")
                            output.write(chunk)
                            remaining -= len(chunk)
            require(seen, "Empty study archive")
        yield root / expected_root


def file_inventory(base):
    """Do not follow symlinks or silently omit special retained objects."""
    files = {}
    for path in sorted(Path(base).rglob("*")):
        require(not path.is_symlink(), "Symlink in study evidence")
        require(path.is_dir() or path.is_file(), "Special file in study evidence")
        if path.is_file():
            name = str(path.relative_to(base))
            if name != "MANIFEST.json":
                files[name] = {"bytes": path.stat().st_size,
                               "sha256": digest(path.read_bytes())}
    return files


def write_manifest(base):
    """Seal existing evidence after execution; never replace an earlier seal."""
    base = Path(base)
    record = {"schema": SCHEMA, "files": file_inventory(base)}
    with (base / "MANIFEST.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    return record


def trial_reader(directory):
    """Bind archived raw bytes. Resource stops may exceed the aggregate cap."""
    inventory = decode_json((directory / "ARTIFACTS.json").read_bytes())
    require(isinstance(inventory, dict) and 0 < len(inventory) <= 5000,
            "Invalid trial artifact inventory")
    cache, stored_names = {}, set()
    for name, item in inventory.items():
        relative(name)
        stored_name = str(relative(item["stored_path"]))
        require(stored_name not in stored_names and stored_name != "ARTIFACTS.json",
                "Aliased stored trial artifact")
        stored_names.add(stored_name)
        path = directory / stored_name
        require(path.is_file() and not path.is_symlink(), "Missing or linked trial artifact")
        for key in ("stored_bytes", "raw_bytes"):
            require(type(item[key]) is int and 0 <= item[key] <= FILE_LIMIT + (1 << 20),
                    "Invalid individual artifact size")
        payload = path.read_bytes()
        require(len(payload) == item["stored_bytes"] and digest(payload) == item["stored_sha256"],
                "Stored trial artifact changed: " + name)
        require(item["encoding"] in ("gzip", "raw"), "Unknown artifact encoding")
        if item["encoding"] == "gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(payload), mode="rb") as stream:
                raw = stream.read(item["raw_bytes"] + 1)
        else:
            raw = payload
        require(len(raw) == item["raw_bytes"] and digest(raw) == item["raw_sha256"],
                "Raw trial artifact changed: " + name)
        cache[name] = raw
    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    require(actual == stored_names | {"ARTIFACTS.json"}, "Unlisted trial artifact")

    def read(name):
        require(name in cache, "Missing retained trial artifact: " + name)
        return cache[name]

    return inventory, read


def validate_protocol(record):
    """Offline validation deliberately does not require the original machine."""
    from research.completion_v1.study import SOURCES, case_records, trial_order
    require(record["schema"] == 1 and
            record["kind"] == "fixed_completion_study_before_measurement", "Unknown study freeze")
    require(record["cases"] == case_records() and record["order"] == trial_order(),
            "Fixed cases/order changed")
    require(set(record["source_files_sha256"]) == set(SOURCES), "Incomplete source freeze")
    for name, expected in record["source_files_sha256"].items():
        require(digest((ROOT / relative(name)).read_bytes()) == expected, "Frozen source changed: " + name)
    qualification_raw = (HERE / "qualification/MANIFEST.json").read_bytes()
    require(digest(qualification_raw) == record["qualification_manifest_sha256"], "Qualification changed")
    require(decode_json(qualification_raw)["binary_sha256"] == record["binary_sha256"],
            "Unqualified executable binding")
    require(record["environment_overrides"] == {"LC_ALL": "C", "PYTHONHASHSEED": "0", "RUST_LOG": "info"}
            and record["seed"] == 0, "Frozen environment changed")
    cpu = record["limits"]["cpu"]
    require(type(cpu) is int and cpu >= 0 and record["limits"] == {
        "cpu": cpu, "wall_seconds": 30.0, "address_space_bytes": 1 << 30,
        "artifact_bytes": FILE_LIMIT, "output_bytes": 1 << 20, "poll_seconds": 0.01},
        "Frozen resource policy changed")


def is_raw(name):
    name = Path(name).name.lower()
    return (Path(name).suffix not in {".json", ".jsonl", ".log", ".stdout", ".stderr"}
            and not name.endswith((".stdout.txt", ".stderr.txt", ".json.tmp")))


def check_stream(observation, stream, content, cap, *, bound_text):
    count = observation[stream + "_bytes"]
    require(type(count) is int and count >= 0 and len(content) == min(count, cap),
            "Unbound stream byte count")
    require(observation[stream + "_truncated"] is (count > cap), "Changed stream truncation flag")
    if bound_text:
        require(observation[stream] == content.decode("utf-8", errors="replace"), "Unbound stream text")


def stage_journal(raw):
    """An interrupted final JSON line is retained, but is not a verdict."""
    rows = []
    lines = raw.splitlines(keepends=True)
    for index, line in enumerate(lines):
        try:
            rows.append(decode_json(line))
        except ValueError:
            require(index == len(lines) - 1 and not line.endswith(b"\n"), "Malformed native stage journal")
    return rows


def validate_trial(row, case, freeze, inventory, read):
    """Validate evidence and derive status; never trust a supplied summary."""
    supervisor = decode_json(read("SUPERVISOR.json"))
    require(supervisor["schema"] == "alc-bounded-workflow-v1" and
            supervisor["limits"] == freeze["limits"] and supervisor["cpu"] == freeze["limits"]["cpu"],
            "Changed supervisor resource policy")
    require(supervisor["instantaneous_aggregate_quota"] is False, "False aggregate quota claim")
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
    require(supervisor["all_trial_files_bytes"] == supervisor["artifact_final_bytes"] == all_bytes and
            supervisor["raw_artifact_bytes"] == raw_bytes, "Retained bytes differ from measured final storage")
    for key in ("artifact_peak_observed_bytes", "open_deleted_peak_observed_bytes",
                "raw_artifact_peak_observed_bytes"):
        require(type(supervisor[key]) is int and supervisor[key] >= 0, "Invalid observed storage peak")
    require(raw_bytes <= supervisor["raw_artifact_peak_observed_bytes"] <= supervisor["artifact_peak_observed_bytes"]
            and all_bytes <= supervisor["artifact_peak_observed_bytes"], "Inconsistent observed storage peaks")
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
        require(total <= 30 and supervisor["artifact_peak_observed_bytes"] <= FILE_LIMIT and
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
            "proofs_replayed": proofs, "sat_assignments_checked": sat}


def audit_unarchived(directory):
    """Recover completed proofs after supervisor infrastructure failure.

    The study-level seal binds these raw files. Missing supervisor accounting
    prevents a trial verdict even when individual CNF proofs check correctly.
    """
    stages = directory / "data/STAGES.jsonl"
    journal = stage_journal(stages.read_bytes()) if stages.is_file() else []
    completed, sat = [], []
    for entry in journal:
        if entry.get("event") != "finish" or entry.get("status") != "completed":
            continue
        command = entry.get("command", [])
        if len(command) < 3 or Path(command[0]).name != "cadical" or entry.get("exit_code") not in (10, 20):
            continue
        name = Path(command[-2]).stem
        require(name in OBLIGATIONS and command[-2:] == [name + ".cnf", name + ".lrat"],
                "Unrecognized partial proof command")
        cnf = (directory / "data" / (name + ".cnf")).read_bytes()
        if entry["exit_code"] == 20:
            proof = (directory / "data" / (name + ".lrat")).read_bytes()
            checked = check_lrat_text(cnf.decode("ascii"), proof.decode("ascii"))
            require(checked["status"] == "verified_unsat", "Partial proof replay failed")
            require(name not in completed, "Duplicate partial proof stage")
            completed.append(name)
        else:
            sat.append({"name": name, **check_sat_assignment(cnf, (directory / "data" / (name + "_solve.stdout.txt")).read_bytes())})
    return completed, sat


def summaries(rows, freeze, complete):
    """Three-of-three is mandatory; a deadline never becomes completion time."""
    groups = []
    by_group = {}
    for case in freeze["cases"]:
        for route in ("exporter", "ric3", "structural"):
            selected = [r for r in rows if r["width"] == case["width"] and r["route"] == route]
            accepted_status = "structural_accepted" if route == "structural" else "accepted"
            finished = [r for r in selected if r["status"] == accepted_status]
            times = [r["wall_seconds"] for r in finished]
            sizes = [r["raw_artifact_bytes"] for r in finished]
            describe = lambda values: ({"median": median(values), "min": min(values), "max": max(values)} if values else None)
            group = {"width": case["width"], "route": route, "observed_trials": len(selected),
                     "accepted_trials": len(finished), "resource_unknown_trials": sum(r["status"] == "resource_unknown" for r in selected),
                     "three_of_three_accepted": len(finished) == 3,
                     "completed_wall_seconds": describe(times), "completed_raw_bytes": describe(sizes)}
            groups.append(group)
            by_group[case["width"], route] = group
    added, reverse = [], []
    for case in freeze["cases"]:
        left, right = (by_group[case["width"], route] for route in ("exporter", "ric3"))
        if left["three_of_three_accepted"] and right["resource_unknown_trials"] == 3:
            added.append(case["width"])
        if right["three_of_three_accepted"] and left["resource_unknown_trials"] == 3:
            reverse.append(case["width"])
    return {"groups": groups, "primary_outcome": "incomplete" if not complete else "added_coverage" if added else "no_added_coverage",
            "exporter_exclusive_widths": added if complete else [], "ric3_exclusive_widths": reverse if complete else [],
            "structural_reference_is_witness_coverage": False}


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
