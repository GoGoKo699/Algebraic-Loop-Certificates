"""Offline binding and independent CNF-proof replay of the frozen five cases.

Source/witness-to-obligation and AIGER-to-CNF translation remain trusted. A
preserved timeout is UNKNOWN, even when earlier obligations have valid proofs.
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
from pathlib import Path

from research.proof_interface_v1.lrat import check_lrat
from .produce import produce
from .model_controls import emit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = HERE / "native"
LIMIT = 64 << 20
OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")
CASES = {
    "rotation3": (3, 0x4, 9, None),
    "mixed5": (5, 0x11, 63, None),
    "published8": (8, 0xb8, 255, None),
    "rotation3_global": (3, 0x4, 9, "global_bound"),
    "mixed5_omit": (5, 0x11, 63, "skip_repeated3"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_native():
    manifest = json.loads((NATIVE / "ARTIFACTS.json").read_text())
    provenance = json.loads((NATIVE / "BUILD_PROVENANCE.json").read_text())
    construction = json.loads((NATIVE / "CONSTRUCTION.json").read_text())
    require(provenance["protocol_sha256"] == sha((HERE / "NATIVE_PROTOCOL.md").read_bytes()), "Frozen protocol changed")
    require(provenance["construction_sha256"] == sha((NATIVE / "CONSTRUCTION.json").read_bytes()), "Construction freeze changed")
    for path, expected in provenance["source_files_sha256"].items():
        require(sha((ROOT / path).read_bytes()) == expected, "Observed driver/constructor source changed: " + path)
    require([c["case"] for c in construction["cases"]] == list(CASES), "Construction case set changed")
    built = {c["case"]: c for c in construction["cases"]}
    stored_names = set()
    totals = {case: 0 for case in CASES}

    def read(name):
        require(name in manifest, "Missing artifact: " + name)
        row = manifest[name]
        path = NATIVE / row["stored_path"]
        require(path.resolve().is_relative_to(NATIVE.resolve()), "Artifact path escapes native directory")
        require(type(row["raw_bytes"]) is int and 0 <= row["raw_bytes"] <= LIMIT, "Invalid raw artifact size")
        require(type(row["stored_bytes"]) is int and 0 <= row["stored_bytes"] <= LIMIT, "Invalid stored artifact size")
        require(path.stat().st_size == row["stored_bytes"], "Stored artifact size changed")
        payload = path.read_bytes()
        require(sha(payload) == row["stored_sha256"], "Stored artifact hash changed: " + name)
        require(row["encoding"] in ("raw", "gzip"), "Unknown artifact encoding")
        if row["encoding"] == "gzip":
            with gzip.open(path, "rb") as stream:
                raw = stream.read(row["raw_bytes"] + 1)
        else:
            raw = payload
        require(len(raw) == row["raw_bytes"] and sha(raw) == row["raw_sha256"], "Raw artifact changed: " + name)
        return raw

    for name, entry in manifest.items():
        parts = Path(name).parts
        require(len(parts) == 2 and parts[0] in CASES and parts[1] not in (".", ".."), "Invalid artifact name")
        require(entry["stored_path"] not in stored_names, "Two artifacts alias one file")
        stored_names.add(entry["stored_path"])
        read(name)
        if Path(name).suffix in (".aag", ".aig", ".cnf", ".lrat"):
            totals[parts[0]] += entry["raw_bytes"]
    require(all(size <= LIMIT for size in totals.values()), "Frozen artifact cap exceeded")
    summaries = []
    for case, (width, taps, multiple, mutation) in CASES.items():
        prefix = case + "/"
        record = json.loads(read(prefix + "RESULTS.json"))
        model, witness = read(prefix + "model.aag"), read(prefix + "witness.aag")
        if width == 8:
            original = (ROOT / "research/aiger_lfsr_v1/upstream/fibonacci-08-0xb8.aag").read_bytes()
            require(model == original, "Published model changed")
            blob = hashlib.sha1(b"blob " + str(len(model)).encode() + b"\0" + model).hexdigest()
            require(blob == "985b32d80f72464ba83b8eb8c975c6b45eab32f2", "Published source blob changed")
        else:
            require(model == emit(width, taps), "Synthetic model differs from independent emitter")
        regenerated, metadata = produce(model, taps, multiple, mutation=mutation)
        require(regenerated == witness, "Witness differs from frozen candidate constructor")
        require(record["input_sha256"] == {"model": sha(model), "witness": sha(witness)}, "Consumed input binding changed")
        construction_row = built[case]
        require(construction_row["returncode"] == 0 and construction_row["model_sha256"] == sha(model)
                and construction_row["witness_sha256"] == sha(witness)
                and construction_row["witness_bytes"] == len(witness), "Construction record differs from consumed candidate")
        require(construction_row["metadata"] == metadata, "Construction metadata changed")
        require(type(construction_row["elapsed_seconds"]) in (float, int)
                and math.isfinite(construction_row["elapsed_seconds"])
                and construction_row["elapsed_seconds"] >= 0, "Invalid construction time")
        require(record["binary_sha256"] == provenance["binary_sha256"], "Tool provenance changed")
        require(record["limits"] == {"seconds_per_process": 10, "address_space_bytes": 1 << 30,
                                    "artifact_bytes_per_case": LIMIT}, "Native limits changed")
        require(record["artifact_bytes"] == totals[case], "Artifact total changed")
        require(record["status"] in ("accepted", "rejected", "unknown"), "Unsupported/incomplete native outcome")
        require(mutation is None or record["status"] != "accepted", "Bad-certificate control unexpectedly accepted")
        require(type(record["elapsed_seconds"]) in (float, int) and math.isfinite(record["elapsed_seconds"])
                and record["elapsed_seconds"] >= 0, "Invalid total native time")
        commands = [("generate", "certifaiger", ["model.aag", "witness.aag", "check.aig"]),
                    ("split", "aigsplit", ["-n", "check.aig", "obligation_"])]
        for name in OBLIGATIONS:
            commands += [(name + "_cnf", "aigtocnf", [name + ".aig", name + ".cnf"]),
                         (name + "_solve", "cadical", ["--quiet", "--unsat", "--lrat", "--no-binary", "--no-factor", name + ".cnf", name + ".lrat"]),
                         (name + "_replay", "lrat-trim", [name + ".cnf", name + ".lrat"])]
        stages = record["stages"]
        require([s["name"] for s in stages] == [c[0] for c in commands[:len(stages)]], "Native stage order changed")
        require(len(stages) <= len(commands) and len(stages) >= 1, "Invalid stage count")
        for s, (_, tool, arguments) in zip(stages, commands):
            require(Path(s["argv"][0]).name == tool and s["argv"][1:] == arguments, "Native invocation changed")
            require(type(s["elapsed_seconds"]) in (float, int) and math.isfinite(s["elapsed_seconds"])
                    and s["elapsed_seconds"] >= 0, "Invalid stage time")
            read(prefix + s["name"] + ".stdout.txt")
            read(prefix + s["name"] + ".stderr.txt")
        for stage in stages[:-1]:
            expected_exit = 20 if stage["name"].endswith(("_solve", "_replay")) else 0
            require(stage["timed_out"] is False and stage["exit_code"] == expected_exit,
                    "Native execution continued after an unsuccessful stage")
        stage_map = {s["name"]: s for s in stages}
        if stage_map["generate"]["exit_code"] == 0:
            read(prefix + "check.aig")
        names = tuple(o["name"] for o in record["obligations"])
        require(names == OBLIGATIONS[:len(names)], "Obligation set duplicated or reordered")
        if "split" in stage_map and stage_map["split"]["exit_code"] == 0:
            for name in OBLIGATIONS:
                read(prefix + name + ".aig")
        replayed = 0
        for obligation in record["obligations"]:
            name = obligation["name"]
            status = obligation["status"]
            require(status in ("unsat_replayed", "sat", "incomplete"), "Unknown obligation status")
            if status == "unsat_replayed":
                for suffix, field in ((".cnf", "cnf_sha256"), (".lrat", "proof_sha256")):
                    require(sha(read(prefix + name + suffix)) == obligation[field], "Proof binding changed")
                require(stage_map[name + "_cnf"]["exit_code"] == 0
                        and stage_map[name + "_solve"]["exit_code"] == 20
                        and stage_map[name + "_replay"]["exit_code"] == 20, "Completed native proof lacks success statuses")
                cnf = NATIVE / manifest[prefix + name + ".cnf"]["stored_path"]
                proof = NATIVE / manifest[prefix + name + ".lrat"]["stored_path"]
                require(check_lrat(cnf, proof)["status"] == "verified_unsat", "Independent LRAT replay failed")
                replayed += 1
            elif status == "sat":
                require(name == names[-1] and record["status"] == "rejected"
                        and stage_map[name + "_solve"]["exit_code"] == 10,
                        "SAT rejection record inconsistent")
                require(b"s SATISFIABLE" in read(prefix + name + "_solve.stdout.txt"), "SAT verdict absent")
            else:
                require(name == names[-1] and record["status"] == "unknown", "Incomplete proof not marked UNKNOWN")
        if record["status"] == "accepted":
            require(names == OBLIGATIONS and replayed == 9 and len(stages) == len(commands), "Acceptance omitted obligations")
            require(all(not s["timed_out"] for s in stages), "Accepted record contains timeout")
            require(stage_map["generate"]["exit_code"] == stage_map["split"]["exit_code"] == 0, "Obligation generation failed")
        elif record["status"] == "rejected":
            require(names and record["obligations"][-1]["status"] == "sat", "Rejection lacks SAT obligation")
        else:
            require(record.get("reason") in ("artifact limit", "native timeout/resource limit"), "Unknown has no resource-limit reason")
            require(totals[case] >= LIMIT or any(s["timed_out"] or (type(s["exit_code"]) is int and s["exit_code"] < 0) for s in stages),
                    "Unknown lacks timeout/resource evidence")
        summaries.append({"case": case, "expected": "accepted" if mutation is None else "rejected",
                          "status": record["status"], "proofs_replayed": replayed,
                          "native_seconds": record["elapsed_seconds"]})
    return {"cases": summaries, "proofs_replayed": sum(r["proofs_replayed"] for r in summaries),
            "scope": "CNF proof replay; native source/witness-to-CNF transformations remain trusted"}


if __name__ == "__main__":
    print(json.dumps(verify_native(), indent=2))
