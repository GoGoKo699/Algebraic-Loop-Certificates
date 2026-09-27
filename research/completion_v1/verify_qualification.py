"""Offline binding and proof replay for the four fixed compatibility smokes.

No native executable is invoked. Independent LRAT replay establishes only CNF
unsatisfiability; the pinned model/witness-to-CNF transformations remain trusted.
Recorded producer output and elapsed times are evidence, not a safety theorem.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath

from research.proof_interface_v1.lrat import Limits, check_lrat_text, parse_cnf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QUALIFICATION = HERE / "qualification"
MODEL = "research/odd_order_witness_v1/models/rotation3.aag"
MODEL_SHA256 = "52cbf63d24a8eb77ece89bf25042be555dc214fbd23cef4680ff93463dd50788"
CASES = ("exporter", "ric3", "exporter_bad", "ric3_bad")
OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")
LIMIT = 64 << 20


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Non-finite JSON token: " + value)

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def relative(name):
    require(isinstance(name, str) and name and "\\" not in name,
            "Invalid artifact path")
    path = PurePosixPath(name)
    require(not path.is_absolute() and str(path) == name and
            all(part not in (".", "..") for part in path.parts), "Artifact path escapes evidence")
    return path


def finite_seconds(value, label):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
            "Invalid time: " + label)
    return value


def artifact_reader(base, artifacts):
    """Validate every stored file and return a bounded, hash-checking reader."""
    base = Path(base).resolve()
    require(isinstance(artifacts, dict) and 0 < len(artifacts) <= 5000,
            "Invalid artifact inventory")
    stored_names = set()
    cache = {}

    def read(name):
        relative(name)
        require(name in artifacts, "Missing retained artifact: " + name)
        if name in cache:
            return cache[name]
        item = artifacts[name]
        stored = base / relative(item["stored_path"])
        require(stored.resolve().is_relative_to(base), "Stored artifact escapes evidence")
        for key in ("raw_bytes", "stored_bytes"):
            require(type(item[key]) is int and 0 <= item[key] <= LIMIT,
                    "Invalid artifact size: " + name)
        require(stored.stat().st_size == item["stored_bytes"], "Stored size changed: " + name)
        payload = stored.read_bytes()
        require(digest(payload) == item["stored_sha256"], "Stored hash changed: " + name)
        require(item["encoding"] in ("raw", "gzip"), "Unknown artifact encoding")
        if item["encoding"] == "gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(payload), mode="rb") as stream:
                raw = stream.read(item["raw_bytes"] + 1)
        else:
            raw = payload
        require(len(raw) == item["raw_bytes"] and digest(raw) == item["raw_sha256"],
                "Raw artifact changed: " + name)
        cache[name] = raw
        return raw

    for name, item in artifacts.items():
        require(item["stored_path"] not in stored_names, "Aliased stored artifact")
        stored_names.add(item["stored_path"])
        read(name)
    actual = {str(path.relative_to(base)) for path in base.rglob("*") if path.is_file()}
    require(actual == stored_names | {"MANIFEST.json"}, "Unlisted or missing evidence file")
    return read


def check_sat_assignment(cnf_raw, stdout_raw):
    """Check the retained negative-control assignment against every CNF clause."""
    variables, clauses, _ = parse_cnf(cnf_raw.decode("ascii"), Limits())
    lines = stdout_raw.decode("ascii").splitlines()
    require([line.strip() for line in lines if line.startswith("s ")] == ["s SATISFIABLE"],
            "Negative control lacks an unambiguous SAT verdict")
    values = []
    for line in lines:
        if line.startswith("v "):
            values.extend(int(token) for token in line.split()[1:])
    require(values and values[-1] == 0 and 0 not in values[:-1], "Malformed SAT assignment")
    assignment = {}
    for literal in values[:-1]:
        require(0 < abs(literal) <= variables, "SAT literal is out of range")
        require(abs(literal) not in assignment, "Duplicate SAT assignment literal")
        assignment[abs(literal)] = literal > 0
    require(all(any(assignment.get(abs(lit)) == (lit > 0) for lit in clause)
                for clause in clauses.values()), "Retained SAT assignment violates a clause")
    return {"variables": variables, "clauses_checked": len(clauses)}


def reconstruct_ric3_mutation(original, mutation):
    """Reproduce the specified single-line corruption, without a solver."""
    lines = original.decode("ascii").splitlines()
    header = lines[0].split()
    require(header[0] == "aag" and 6 <= len(header) <= 10, "Unsupported smoke witness header")
    numbers = [int(token) for token in header[1:]]
    _, inputs, latches, outputs, _ = numbers[:5]
    if mutation["kind"] == "mapped_reset_flip":
        index = mutation["latch_index"]
        require(type(index) is int and 0 <= index < latches, "Invalid mutated latch")
        require(mutation["before"] == "0" and mutation["after"] == "1", "Changed reset mutation")
        symbols = [line.split() for line in lines if line.startswith(f"l{index} ")]
        require(len(symbols) == 1 and len(symbols[0]) == 3 and symbols[0][1] == "=",
                "Mutated latch lacks an original-latch mapping")
        require(int(symbols[0][2]) in range(8, 21, 2), "Mutated latch maps outside original latches")
        at = 1 + inputs + index
        row = lines[at].split()
        require(len(row) in (2, 3) and (len(row) == 2 or row[2] == "0"),
                "Original witness latch was not zero initialized")
        lines[at] = " ".join(row[:2] + ["1"])
    elif mutation["kind"] == "constant_bad":
        extra = numbers[5:] + [0] * (4 - len(numbers[5:]))
        bads, constraints, justice, fairness = extra
        require(constraints == justice == fairness == 0 and outputs + bads == 1,
                "Constant-bad control requires one unconstrained safety property")
        at = 1 + inputs + latches
        require(lines[at] != "1", "Original property is already constant bad")
        lines[at] = "1"
    else:
        raise ValueError("Unknown rIC3 witness mutation")
    return ("\n".join(lines) + "\n").encode("ascii")


def native_commands(rejected_obligation):
    rows = [("generate", "certifaiger", ["model.aag", "witness.aag", "check.aig"], 0),
            ("split", "aigsplit", ["-n", "check.aig", "obligation_"], 0)]
    names = OBLIGATIONS if rejected_obligation is None else OBLIGATIONS[:OBLIGATIONS.index(rejected_obligation) + 1]
    for name in names:
        rows.append((name + "_cnf", "aigtocnf", [name + ".aig", name + ".cnf"], 0))
        rows.append((name + "_solve", "cadical", ["--quiet", "--unsat", "--lrat",
                     "--no-binary", "--no-factor", name + ".cnf", name + ".lrat"],
                     10 if name == rejected_obligation else 20))
        if name != rejected_obligation:
            rows.append((name + "_replay", "lrat-trim", [name + ".cnf", name + ".lrat"], 20))
    return rows, names


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
        require(isinstance(case["mutation"], dict), "Missing rIC3 corruption")
        if case["mutation"]["kind"] == "mapped_reset_flip":
            require(rejected == "Reset", "Reset corruption rejected at unexpected obligation")
        else:
            require(case["mutation"]["kind"] == "constant_bad" and rejected in ("Base", "Safety"),
                    "Unsupported rIC3 bad-property control")
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

    require(supervisor["schema"] == "alc-bounded-workflow-v1" and
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
            limits["artifact_bytes"] == LIMIT and limits["output_bytes"] == 1 << 20 and
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
    for key in ("artifact_peak_observed_bytes", "artifact_final_bytes", "open_deleted_peak_observed_bytes",
                "raw_artifact_bytes", "raw_artifact_peak_observed_bytes", "all_trial_files_bytes"):
        require(type(supervisor[key]) is int and 0 <= supervisor[key] <= LIMIT,
                "Completed smoke has an invalid or exceeded storage observation")
    require(supervisor["artifact_peak_observed_bytes"] >= supervisor["artifact_final_bytes"],
            "Storage peak is below the final observation")
    require(supervisor["artifact_final_bytes"] == supervisor["all_trial_files_bytes"] and
            supervisor["raw_artifact_bytes"] <= supervisor["raw_artifact_peak_observed_bytes"] <=
            supervisor["artifact_peak_observed_bytes"], "Raw/all-file storage observations disagree")
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
    """Cross-bind the recorded executable hashes to their retained build records."""
    require(manifest["environment_overrides"] == {"LC_ALL": "C", "PYTHONHASHSEED": "0", "RUST_LOG": "info"},
            "Qualification environment overrides changed")
    native = manifest["native_checker_provenance"]
    require(native == {
        "path": "research/odd_order_witness_v1/native/BUILD_PROVENANCE.json",
        "sha256": "488c456a8cfe5d2db8d4ebb9ab62fd04084a461de0a3c29ac5ba041bfc48eb67"},
        "Native checker no longer binds the unchanged Gate 12 build")
    raw = (ROOT / native["path"]).read_bytes()
    require(digest(raw) == native["sha256"], "Historical native build provenance changed")
    previous = decode_json(raw)
    require({name: value for name, value in manifest["binary_sha256"].items() if name != "ric3"}
            == previous["binary_sha256"], "Native checker binary hashes differ from Gate 12")
    require(manifest["ric3_build"] == "build/BUILD_PROVENANCE.json", "Changed rIC3 build record location")
    build = decode_json(read(manifest["ric3_build"]))
    require(build["schema"] == "ric3-pinned-build-v1" and
            build["source"]["commit"] == "8dcec6995e0e5c0adf7d4397047aafc06e9559dc" and
            build["source"]["dirty"] is False and build["source"]["dirty_after_build"] is False,
            "rIC3 source pin or clean-build observation changed")
    require(build["binary"]["sha256"] == manifest["binary_sha256"]["ric3"] and
            build["binary"]["version"] == "rIC3 1.5.2", "rIC3 executable provenance differs")
    require(build["build"]["command"] == ["cargo", "build", "--release", "--locked", "--offline", "-j", "2"],
            "Recorded rIC3 build command changed")
    lock = read("build/Cargo.lock")
    require(digest(lock) == build["source"]["cargo_lock_sha256"] and
            hashlib.sha1(b"blob " + str(len(lock)).encode() + b"\0" + lock).hexdigest()
            == build["source"]["cargo_lock_git_blob"], "rIC3 dependency lock changed")
    require(digest(read("build/build-release.log")) == build["build"]["log_sha256"],
            "rIC3 build log changed")
    require(read("build/version.txt").decode().strip() == build["binary"]["version"],
            "rIC3 executable version observation changed")


def verify_qualification(base=QUALIFICATION):
    base = Path(base)
    manifest = decode_json((base / "MANIFEST.json").read_bytes())
    require(manifest["schema"] == 1 and manifest["model"] == {
        "repository_path": MODEL, "sha256": MODEL_SHA256}, "Qualification manifest/model changed")
    require(digest((ROOT / MODEL).read_bytes()) == MODEL_SHA256, "Original synthetic fixture changed")
    require([case["id"] for case in manifest["cases"]] == list(CASES), "Fixed smoke controls changed")
    required_sources = {"research/completion_v1/worker.py", "research/completion_v1/resources.py",
                        "research/odd_order_witness_v1/produce.py", "research/proof_interface_v1/produce.py",
                        "research/aiger_lfsr_v1/check.py", "research/aiger_lfsr_v1/source_aware.py",
                        "research/proof_interface_v1/lrat.py"}
    require(required_sources <= set(manifest["source_files_sha256"]), "Missing workflow/checker source binding")
    for name, expected in manifest["source_files_sha256"].items():
        require(digest((ROOT / relative(name)).read_bytes()) == expected, "Frozen source changed: " + name)
    binaries = manifest["binary_sha256"]
    require({"ric3", "certifaiger", "aigsplit", "aigtocnf", "cadical", "lrat-trim"} <= set(binaries),
            "Missing native binary provenance")
    for value in binaries.values():
        require(isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value),
                "Malformed native binary hash")
    read = artifact_reader(base, manifest["artifacts"])
    validate_provenance(manifest, read)
    rows = []
    for case in manifest["cases"]:
        record = decode_json(read(case["worker_result"]))
        supervisor = decode_json(read(case["supervisor_result"]))
        files = {name: item for name, item in manifest["artifacts"].items()
                 if name.startswith(case["id"] + "/") and name != case["supervisor_result"]}
        require(sum(item["raw_bytes"] for item in files.values()) == supervisor["all_trial_files_bytes"],
                "Retained all-file bytes differ from measured final storage")
        require(sum(item["raw_bytes"] for name, item in files.items()
                    if Path(name).suffix in (".aag", ".aig", ".cnf", ".lrat")) == supervisor["raw_artifact_bytes"],
                "Retained raw circuit/proof bytes differ from measured final storage")
        rows.append(validate_case(case, record, supervisor, read))
    require(sum(row["status"] == "accepted" for row in rows) == 2 and
            sum(row["status"] == "rejected" for row in rows) == 2, "Incomplete compatibility qualification")
    return {"cases": rows, "proofs_replayed": sum(row["proofs_replayed"] for row in rows),
            "negative_assignments_checked": sum(row["sat_assignment"] is not None for row in rows),
            "checked_artifact_files": len(manifest["artifacts"]),
            "boundary": "CNF proofs and SAT controls checked independently; native translations remain trusted"}


if __name__ == "__main__":
    print(json.dumps(verify_qualification(), indent=2))
