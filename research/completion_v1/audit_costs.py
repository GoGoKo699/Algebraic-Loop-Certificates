"""Decompose eight preserved native runs; perform no new experiment or proof check.

Decimal arithmetic preserves the JSON timing tokens, not additional measurement
precision. Construction observations remain separate: Gate 11 phase timings were
measured after native replay, and its ABC adapter time was never measured. Even
Gate 12's pre-run construction and native timings are separately scoped records,
not a single complete end-to-end measurement. No combined workflow total is made.

This is an analytical report, not a certificate format or safety acceptance API.
Existing native verifiers remain responsible for source binding and proof replay.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / "COST_AUDIT.json"
OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")
CASES = (
    (11, "proof_interface_v1", "abc02", 2, "abc_export"),
    (11, "proof_interface_v1", "abc04", 4, "abc_export"),
    (11, "proof_interface_v1", "phase02", 2, "maximal_phase"),
    (11, "proof_interface_v1", "phase04", 4, "maximal_phase"),
    (11, "proof_interface_v1", "phase08", 8, "maximal_phase"),
    (12, "odd_order_witness_v1", "rotation3", 3, "exact_seed_period"),
    (12, "odd_order_witness_v1", "mixed5", 5, "exact_seed_period"),
    (12, "odd_order_witness_v1", "published8", 8, "exact_seed_period"),
)
GROUPS = ("obligation_generation", "obligation_split", "cnf_conversion",
          "sat_search_and_lrat_emission", "native_lrat_replay")
LIMIT = 64 << 20


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("Non-finite JSON token: " + value)


def decode_json(raw):
    return json.loads(raw, parse_float=Decimal, parse_constant=invalid_constant,
                      object_pairs_hook=unique_object)


def seconds(value):
    require(type(value) in (int, Decimal), "Time must be a JSON number")
    value = Decimal(value)
    require(value.is_finite() and value >= 0, "Invalid elapsed time")
    require(len(value.as_tuple().digits) <= 64 and abs(value.as_tuple().exponent) <= 64,
            "Timing token exceeds exact arithmetic bounds")
    return value


def natural(value, label):
    require(type(value) is int and value >= 0, "Invalid integer: " + label)
    return value


def decimal_text(value):
    return format(value, "f")


def expected_stages():
    rows = [("generate", "certifaiger", ["model.aag", "witness.aag", "check.aig"],
             0, "obligation_generation"),
            ("split", "aigsplit", ["-n", "check.aig", "obligation_"],
             0, "obligation_split")]
    for name in OBLIGATIONS:
        rows.extend((
            (name + "_cnf", "aigtocnf", [name + ".aig", name + ".cnf"],
             0, "cnf_conversion"),
            (name + "_solve", "cadical", ["--quiet", "--unsat", "--lrat",
             "--no-binary", "--no-factor", name + ".cnf", name + ".lrat"],
             20, "sat_search_and_lrat_emission"),
            (name + "_replay", "lrat-trim", [name + ".cnf", name + ".lrat"],
             20, "native_lrat_replay"),
        ))
    return rows


def validate_record(record, binary_hashes):
    """Validate recorded completion and return exact timing groups, not SAFE."""
    require(type(record["schema"]) is int and record["schema"] == 1,
            "Unsupported native observation schema")
    require(record["interface"] == "existing Certifaiger AIGER witness circuits",
            "Native interface changed")
    require(record["status"] == "accepted", "Expected an accepted positive observation")
    require(record["binary_sha256"] == binary_hashes, "Native binary provenance changed")
    require(record["limits"] == {"seconds_per_process": 10, "address_space_bytes": 1 << 30,
                                  "artifact_bytes_per_case": LIMIT}, "Native limits changed")
    require(tuple(row["name"] for row in record["obligations"]) == OBLIGATIONS,
            "Missing, duplicate, or reordered obligation")
    require(all(row["status"] == "unsat_replayed" for row in record["obligations"]),
            "An obligation lacks recorded replay")
    expected = expected_stages()
    require(len(record["stages"]) == len(expected), "Incomplete native stage list")
    groups = {name: Decimal(0) for name in GROUPS}
    by_name = {}
    for row, (name, tool, arguments, code, group) in zip(record["stages"], expected):
        require(row["name"] == name, "Native stage sequence changed")
        require(type(row["exit_code"]) is int and row["exit_code"] == code
                and row["timed_out"] is False, "Native stage did not succeed")
        require(Path(row["argv"][0]).name == tool and row["argv"][1:] == arguments,
                "Native stage command changed")
        elapsed = seconds(row["elapsed_seconds"])
        groups[group] += elapsed
        by_name[name] = elapsed
    native = seconds(record["elapsed_seconds"])
    stage_sum = sum(groups.values(), Decimal(0))
    require(native >= stage_sum, "Native total is smaller than its stage sum")
    return groups, by_name, native, native - stage_sum


def audit():
    source_hashes = {}

    def read(path):
        path = path.resolve()
        require(path.is_relative_to(ROOT), "Input escapes repository")
        raw = path.read_bytes()
        source_hashes[str(path.relative_to(ROOT))] = sha(raw)
        return raw

    def load(path):
        return decode_json(read(path))

    native_roots = {module: ROOT / "research" / module / "native"
                    for _, module, *_ in CASES}
    manifests = {module: load(path / "ARTIFACTS.json")
                 for module, path in native_roots.items()}
    provenance = {module: load(path / "BUILD_PROVENANCE.json")
                  for module, path in native_roots.items()}
    common_binaries = provenance["proof_interface_v1"]["binary_sha256"]
    require(provenance["odd_order_witness_v1"]["binary_sha256"] == common_binaries,
            "Native tools differ between gates")

    def artifact_metadata(module, name):
        row = manifests[module][name]
        natural(row["raw_bytes"], "artifact raw bytes")
        natural(row["stored_bytes"], "artifact stored bytes")
        require(row["raw_bytes"] <= LIMIT and row["stored_bytes"] <= LIMIT,
                "Artifact exceeds retained cap")
        require(row["encoding"] in ("raw", "gzip"), "Unknown artifact encoding")
        path = (native_roots[module] / row["stored_path"]).resolve()
        require(path.is_relative_to(native_roots[module]), "Artifact path escapes native directory")
        return row, path

    def read_small_artifact(module, name):
        row, path = artifact_metadata(module, name)
        require(row["raw_bytes"] <= 1 << 20, "Unexpected large metadata/model/witness")
        payload = read(path)
        require(len(payload) == row["stored_bytes"] and sha(payload) == row["stored_sha256"],
                "Stored analytical input changed")
        if row["encoding"] == "gzip":
            with gzip.open(path, "rb") as stream:
                raw = stream.read(row["raw_bytes"] + 1)
        else:
            raw = payload
        require(len(raw) == row["raw_bytes"] and sha(raw) == row["raw_sha256"],
                "Raw analytical input changed")
        return raw

    phase_record = load(native_roots["proof_interface_v1"] / "CONSTRUCTION_PHASE.json")
    require(phase_record["original_construction_time_measured"] is False,
            "Gate 11 construction scope changed")
    phase_cases = {row["case"]: row for row in phase_record["cases"]}
    require(set(phase_cases) == {"phase02", "phase04", "phase08"}
            and len(phase_record["cases"]) == 3, "Phase reconstruction cases changed")
    abc_scope = load(native_roots["proof_interface_v1"] / "CONSTRUCTION_ABC.json")
    require(abc_scope["abc_export_time_measured"] is True
            and abc_scope["original_pla_to_witness_time_measured"] is False,
            "ABC construction scope changed")
    abc_export = load(native_roots["proof_interface_v1"] / "abc_export/EXPORT_RESULTS.json")
    abc_cases = {row["n"]: row for row in abc_export["results"]}
    require(set(abc_cases) == {2, 4} and len(abc_export["results"]) == 2,
            "ABC export cases changed")
    odd_path = native_roots["odd_order_witness_v1"] / "CONSTRUCTION.json"
    odd_raw = read(odd_path)
    require(sha(odd_raw) == provenance["odd_order_witness_v1"]["construction_sha256"],
            "Gate 12 construction freeze changed")
    odd_record = decode_json(odd_raw)
    odd_cases = {row["case"]: row for row in odd_record["cases"]}
    require(list(odd_cases) == ["rotation3", "mixed5", "published8", "rotation3_global", "mixed5_omit"]
            and len(odd_record["cases"]) == 5, "Gate 12 construction cases changed")

    cases = []
    total_groups = {name: Decimal(0) for name in GROUPS}
    total_native = total_overhead = Decimal(0)
    total_witness = total_cnf = total_proof = 0
    with localcontext() as context:
        context.prec = 160
        for gate, module, case, width, method in CASES:
            prefix = case + "/"
            record = decode_json(read_small_artifact(module, prefix + "RESULTS.json"))
            groups, stages, native, overhead = validate_record(record, common_binaries)
            model = read_small_artifact(module, prefix + "model.aag")
            witness = read_small_artifact(module, prefix + "witness.aag")
            require(record["input_sha256"] == {"model": sha(model), "witness": sha(witness)},
                    "Observed model/witness binding changed")
            require(model.splitlines()[0].split()[2] == str(width).encode(), "Source width changed")
            artifact_total = sum(artifact_metadata(module, name)[0]["raw_bytes"]
                                 for name in manifests[module]
                                 if name.startswith(prefix) and Path(name).suffix in (".aag", ".aig", ".cnf", ".lrat"))
            require(record["artifact_bytes"] == artifact_total <= LIMIT, "Recorded artifact total changed")
            obligations = []
            for obligation in record["obligations"]:
                name = obligation["name"]
                for suffix, size_key, hash_key in ((".cnf", "cnf_bytes", "cnf_sha256"),
                                                   (".lrat", "proof_bytes", "proof_sha256")):
                    entry, _ = artifact_metadata(module, prefix + name + suffix)
                    require(natural(obligation[size_key], size_key) == entry["raw_bytes"]
                            and obligation[hash_key] == entry["raw_sha256"],
                            "Obligation artifact metadata changed")
                obligations.append({"name": name, "raw_cnf_bytes": obligation["cnf_bytes"],
                                    "raw_lrat_bytes": obligation["proof_bytes"],
                                    "cnf_seconds": decimal_text(stages[name + "_cnf"]),
                                    "search_and_emission_seconds": decimal_text(stages[name + "_solve"]),
                                    "native_lrat_replay_seconds": decimal_text(stages[name + "_replay"])})
            if method == "abc_export":
                entry = abc_cases[width]
                require(entry["returncode"] == 0, "ABC export failed")
                construction = {
                    "kind": "partial_original_abc_search_and_pla_export",
                    "seconds": decimal_text(seconds(entry["wall_seconds"])),
                    "source": "research/proof_interface_v1/native/abc_export/EXPORT_RESULTS.json",
                    "missing": ["original AAG-to-binary preparation", "PLA-to-AIGER adaptation"],
                    "complete_original_construction_measured": False,
                }
            elif method == "maximal_phase":
                entry = phase_cases[case]
                require(entry["returncode"] == 0 and entry["byte_identical_to_preserved_native_witness"] is True
                        and entry["model_sha256"] == sha(model) and entry["output_sha256"] == sha(witness)
                        and entry["output_bytes"] == len(witness), "Post-replay reconstruction binding changed")
                construction = {
                    "kind": "post_native_byte_identical_reconstruction",
                    "seconds": decimal_text(seconds(entry["full_cold_process_elapsed_seconds"])),
                    "source": "research/proof_interface_v1/native/CONSTRUCTION_PHASE.json",
                    "complete_original_construction_measured": False,
                    "add_to_native_total": False,
                }
            else:
                entry = odd_cases[case]
                require(entry["returncode"] == 0 and entry["model_sha256"] == sha(model)
                        and entry["witness_sha256"] == sha(witness) and entry["witness_bytes"] == len(witness),
                        "Pre-native construction binding changed")
                construction = {
                    "kind": "pre_native_fresh_process_source_to_witness",
                    "seconds": decimal_text(seconds(entry["elapsed_seconds"])),
                    "source": "research/odd_order_witness_v1/native/CONSTRUCTION.json",
                    "complete_original_construction_measured": True,
                    "scope": odd_record["timing_scope"],
                }
            cnf_bytes = sum(row["raw_cnf_bytes"] for row in obligations)
            proof_bytes = sum(row["raw_lrat_bytes"] for row in obligations)
            cases.append({
                "gate": gate, "case": case, "method": method, "source_width": width,
                "source_kind": "synthetic_premise_control" if case in ("rotation3", "mixed5") else "published_original",
                "obligations": obligations, "native_stage_count": len(record["stages"]),
                "native_seconds": decimal_text(native),
                "native_stage_seconds": {name: decimal_text(value) for name, value in groups.items()},
                "native_unallocated_overhead_seconds": decimal_text(overhead),
                "construction_observation": construction,
                "complete_original_end_to_end_seconds": None,
                "witness_bytes": len(witness), "raw_cnf_bytes": cnf_bytes,
                "raw_lrat_bytes": proof_bytes, "raw_case_artifact_bytes": artifact_total,
                "results_path": str((native_roots[module] / case / "RESULTS.json").relative_to(ROOT)),
            })
            for name in GROUPS:
                total_groups[name] += groups[name]
            total_native += native
            total_overhead += overhead
            total_witness += len(witness)
            total_cnf += cnf_bytes
            total_proof += proof_bytes
        require(sum(total_groups.values(), total_overhead) == total_native, "Cost decomposition does not close")

    return {
        "report_version": 1,
        "purpose": "Arithmetic decomposition of preserved Gate 11/12 observations; no new experiment",
        "timing_encoding": "Exact decimal strings from recorded JSON tokens; digits do not imply clock precision",
        "native_timing_scope": "Recorded driver interval after copying/hashing inputs: obligation generation, splitting, CNF conversion, SAT search/proof emission, native LRAT replay, and intervening orchestration. Excludes producer work, tool builds, later Python replay and report generation.",
        "limitations": [
            "One preserved native observation per case; caches were not controlled and no statistical speedup is established.",
            "The eight cases are different methods/gates and include repeated source models, not eight independent benchmark instances.",
            "Gate 11 phase construction was measured after native replay; original ABC adaptation cost is missing.",
            "No complete original end-to-end total is reported, including for separately timed Gate 12 construction and replay.",
            "SAT search stages include LRAT emission; replay stages measure only native lrat-trim processes.",
            "Artifact sizes come from retained manifests cross-checked with obligation records; this audit does not replay LRAT or establish safety.",
        ],
        "counts": {"accepted_positive_observations": len(cases), "obligations": len(cases) * len(OBLIGATIONS),
                   "native_stages": sum(row["native_stage_count"] for row in cases)},
        "sums_of_recorded_observations": {
            "native_seconds": decimal_text(total_native),
            "native_stage_seconds": {name: decimal_text(value) for name, value in total_groups.items()},
            "native_unallocated_overhead_seconds": decimal_text(total_overhead),
            "witness_bytes": total_witness, "raw_cnf_bytes": total_cnf, "raw_lrat_bytes": total_proof,
        },
        "cases": cases,
        "source_files_sha256": dict(sorted(source_hashes.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--check", action="store_true", help="Compare against the committed analytical report")
    options.add_argument("--output", type=Path, help="Write a new report, refusing to overwrite")
    args = parser.parse_args()
    serialized = json.dumps(audit(), indent=2, sort_keys=True) + "\n"
    if args.check:
        require(REPORT.read_text() == serialized, "Committed cost audit differs from preserved observations")
        print("PASS: 8 preserved observations, 72 obligations and 232 stages; no native execution or proof replay.")
    elif args.output:
        with args.output.open("x") as stream:
            stream.write(serialized)
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
