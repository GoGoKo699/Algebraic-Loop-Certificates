"""Offline byte binding and independent RUP replay of the native evidence.

The AIGER-to-CNF translation remains a trusted native step. Replaying a CNF
proof does not independently validate that translation; its exact artifacts
and tool provenance are bound by hashes, with this boundary stated explicitly.
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from research.proof_interface_v1.lrat import check_lrat
from research.proof_interface_v1.produce import produce

HERE = Path(__file__).resolve().parent
NATIVE = HERE / "native"
LIMIT = 64 << 20
OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")
CASES = {"abc02": (2, None), "abc04": (4, None),
         "phase02": (2, None), "phase04": (4, None), "phase08": (8, None),
         "bad_zero02": (2, "Safety"), "reset_flipped02": (2, "Reset"),
         "freeze_phase04": (4, "Inductive"), "inverted_phase04": (4, "Inductive")}
MODELS = {2: "fibonacci-02-0x3.aag", 4: "fibonacci-04-0xc.aag", 8: "fibonacci-08-0xb8.aag"}
MODEL_BLOBS = {2: "492d5e8ed0f745bb32b9074893cf27d7bf42805a",
               4: "908ebd7b513afa29385671c07e71167eaf1df90d",
               8: "985b32d80f72464ba83b8eb8c975c6b45eab32f2"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_native():
    manifest = json.loads((NATIVE / "ARTIFACTS.json").read_text())
    provenance = json.loads((NATIVE / "BUILD_PROVENANCE.json").read_text())
    require(provenance["protocol_sha256"] == digest((HERE / "NATIVE_PROTOCOL.md").read_bytes()),
            "Frozen native protocol changed")
    stored_names = set()
    total_bytes = {}

    def read(name):
        require(name in manifest, "Missing artifact: " + name)
        row = manifest[name]
        stored = NATIVE / row["stored_path"]
        require(stored.resolve().is_relative_to(NATIVE.resolve()), "Artifact path escapes native directory")
        require(type(row["raw_bytes"]) is int and 0 <= row["raw_bytes"] <= LIMIT,
                "Invalid raw artifact size")
        require(type(row["stored_bytes"]) is int and 0 <= row["stored_bytes"] <= LIMIT,
                "Invalid stored artifact size")
        require(stored.stat().st_size == row["stored_bytes"], "Stored artifact size changed: " + name)
        payload = stored.read_bytes()
        require(digest(payload) == row["stored_sha256"], "Stored artifact hash changed: " + name)
        require(row["encoding"] in ("raw", "gzip"), "Unknown artifact encoding")
        if row["encoding"] == "gzip":
            with gzip.open(stored, "rb") as stream:
                raw = stream.read(row["raw_bytes"] + 1)
        else:
            raw = payload
        require(len(raw) == row["raw_bytes"] and digest(raw) == row["raw_sha256"],
                "Raw artifact bytes changed: " + name)
        return raw

    for name, row in manifest.items():
        parts = Path(name).parts
        require(len(parts) == 2 and parts[0] in CASES and parts[1] not in (".", ".."),
                "Unexpected artifact name")
        require(row["stored_path"] not in stored_names, "Two artifacts share one stored path")
        stored_names.add(row["stored_path"])
        read(name)
        if Path(name).suffix in (".aag", ".aig", ".cnf", ".lrat"):
            total_bytes[parts[0]] = total_bytes.get(parts[0], 0) + row["raw_bytes"]
    require(all(n <= LIMIT for n in total_bytes.values()), "Case exceeds frozen artifact limit")
    rows = []
    for case, (width, rejected_obligation) in CASES.items():
        prefix = case + "/"
        result = json.loads(read(prefix + "RESULTS.json"))
        model, witness = read(prefix + "model.aag"), read(prefix + "witness.aag")
        expected_model = (ROOT / "research/aiger_lfsr_v1/upstream" / MODELS[width]).read_bytes()
        require(model == expected_model, "Consumed model differs from original fixture")
        blob = hashlib.sha1(b"blob " + str(len(model)).encode() + b"\0" + model).hexdigest()
        require(blob == MODEL_BLOBS[width], "Consumed model differs from pinned upstream blob")
        mutation = {"freeze_phase04": "freeze_phase", "inverted_phase04": "inverted_phase"}.get(case)
        if case.startswith("phase") or mutation:
            regenerated, _ = produce(model, {2: 0x3, 4: 0xc, 8: 0xb8}[width], mutation=mutation)
            require(regenerated == witness, "Native witness differs from current untrusted constructor output")
        require(result["input_sha256"] == {"model": digest(model), "witness": digest(witness)},
                "Consumed input binding changed")
        require(result["binary_sha256"] == provenance["binary_sha256"], "Native binary provenance changed")
        require(result["limits"] == {"seconds_per_process": 10, "address_space_bytes": 1 << 30,
                                     "artifact_bytes_per_case": LIMIT}, "Native limits changed")
        require(result["artifact_bytes"] == total_bytes[case], "Recorded raw artifact total changed")
        expected_names = OBLIGATIONS if rejected_obligation is None else OBLIGATIONS[:OBLIGATIONS.index(rejected_obligation) + 1]
        require(tuple(row["name"] for row in result["obligations"]) == expected_names,
                "Missing, duplicated, or reordered obligations")
        require(result["status"] == ("accepted" if rejected_obligation is None else "rejected"),
                "Unexpected native verdict")
        stages = result["stages"]
        require(len({row["name"] for row in stages}) == len(stages), "Duplicate native stage")
        stage_map = {row["name"]: row for row in stages}
        require(all(not row["timed_out"] for row in stages), "Completed record contains a timeout")
        require(all(isinstance(row["elapsed_seconds"], (int, float)) and
                    math.isfinite(row["elapsed_seconds"]) and row["elapsed_seconds"] >= 0
                    for row in stages), "Invalid native elapsed time")
        require(isinstance(result["elapsed_seconds"], (int, float)) and
                math.isfinite(result["elapsed_seconds"]) and result["elapsed_seconds"] >= 0,
                "Invalid total elapsed time")
        expected_commands = [("generate", "certifaiger", ["model.aag", "witness.aag", "check.aig"]),
                             ("split", "aigsplit", ["-n", "check.aig", "obligation_"])]
        for name in expected_names:
            expected_commands += [(name + "_cnf", "aigtocnf", [name + ".aig", name + ".cnf"]),
                                  (name + "_solve", "cadical", ["--quiet", "--unsat", "--lrat",
                                   "--no-binary", "--no-factor", name + ".cnf", name + ".lrat"])]
            if name != rejected_obligation:
                expected_commands.append((name + "_replay", "lrat-trim", [name + ".cnf", name + ".lrat"]))
        require([row["name"] for row in stages] == [row[0] for row in expected_commands],
                "Native stage sequence is incomplete or changed")
        for row, (_, tool, arguments) in zip(stages, expected_commands):
            require(Path(row["argv"][0]).name == tool and row["argv"][1:] == arguments,
                    "Native invocation changed")
        require(stage_map["generate"]["exit_code"] == stage_map["split"]["exit_code"] == 0,
                "Native obligation construction failed")
        for filename in ("check.aig",) + tuple(name + ".aig" for name in OBLIGATIONS):
            read(prefix + filename)
        replay_count = 0
        for obligation in result["obligations"]:
            name = obligation["name"]
            require(stage_map[name + "_cnf"]["exit_code"] == 0, "CNF generation did not finish")
            if name == rejected_obligation:
                require(obligation["status"] == "sat" and stage_map[name + "_solve"]["exit_code"] == 10,
                        "Invalid witness was not rejected by a SAT obligation")
                require(b"s SATISFIABLE" in read(prefix + name + "_solve.stdout.txt"),
                        "Native rejection lacks SAT verdict")
                continue
            require(obligation["status"] == "unsat_replayed", "Proof was not replayed")
            require(stage_map[name + "_solve"]["exit_code"] == stage_map[name + "_replay"]["exit_code"] == 20,
                    "Native solver or LRAT checker did not accept")
            for suffix, hash_field in ((".cnf", "cnf_sha256"), (".lrat", "proof_sha256")):
                require(digest(read(prefix + name + suffix)) == obligation[hash_field],
                        "Obligation proof binding changed")
            cnf = NATIVE / manifest[prefix + name + ".cnf"]["stored_path"]
            proof = NATIVE / manifest[prefix + name + ".lrat"]["stored_path"]
            checked = check_lrat(cnf, proof)
            require(checked["status"] == "verified_unsat", "Independent proof replay failed")
            replay_count += 1
        rows.append({"case": case, "status": result["status"], "proofs_replayed": replay_count})
    require(sum(row["proofs_replayed"] for row in rows) == 57, "Not all recorded completed proofs replayed")
    abc_dir = NATIVE / "abc_export"
    abc_manifest = json.loads((abc_dir / "MANIFEST.json").read_text())
    for item in abc_manifest["files"]:
        path = abc_dir / item["path"]
        require(path.resolve().is_relative_to(abc_dir.resolve()), "ABC provenance path escapes directory")
        raw = path.read_bytes()
        require(len(raw) == item["bytes"] and digest(raw) == item["sha256"],
                "ABC export/adapter provenance changed")
    for width in (2, 4):
        label = f"n{width:02d}"
        consumed = read(f"abc{width:02d}/witness.aag")
        conversion = json.loads((abc_dir / (label + "-conversion.json")).read_text())
        require((abc_dir / (label + "-witness.aag")).read_bytes() == consumed and
                conversion["witness_sha256"] == digest(consumed), "ABC witness construction binding changed")
    construction = json.loads((NATIVE / "CONSTRUCTION_PHASE.json").read_text())
    require([row["case"] for row in construction["cases"]] == ["phase02", "phase04", "phase08"],
            "Missing phase reconstruction observation")
    for item in construction["cases"]:
        consumed = read(item["case"] + "/witness.aag")
        require(item["returncode"] == 0 and item["output_sha256"] == digest(consumed)
                and item["output_bytes"] == len(consumed), "Phase construction record differs from consumed witness")
    return {"cases": rows, "positive_proofs": 45, "negative_prefix_proofs": 12,
            "checked_artifact_files": len(manifest),
            "boundary": "Independent CNF/RUP replay; native model-to-CNF translation remains trusted"}


if __name__ == "__main__":
    print(json.dumps(verify_native(), indent=2))
