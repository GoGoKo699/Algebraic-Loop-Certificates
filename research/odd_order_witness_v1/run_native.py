"""Freeze construction records, then reuse the unchanged Gate 11 native driver.

Prepare and execute are separate explicit commands. Execution never regenerates
a candidate or changes a limit. Existing case directories are never overwritten.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = HERE / "native"
DRIVER = ROOT / "research/proof_interface_v1/run_native.py"
CASES = (
    ("rotation3", "models/rotation3.aag", 0x4, 9, None),
    ("mixed5", "models/mixed5.aag", 0x11, 63, None),
    ("published8", "../aiger_lfsr_v1/upstream/fibonacci-08-0xb8.aag", 0xb8, 255, None),
    ("rotation3_global", "models/rotation3.aag", 0x4, 9, "global_bound"),
    ("mixed5_omit", "models/mixed5.aag", 0x11, 63, "skip_repeated3"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(tools):
    require(not NATIVE.exists(), "Refusing to overwrite prepared evidence")
    old = json.loads((ROOT / "research/proof_interface_v1/native/BUILD_PROVENANCE.json").read_text())
    for name, expected in old["binary_sha256"].items():
        require(sha(tools / name) == expected, "Native tool differs from Gate 11: " + name)
    NATIVE.mkdir()
    (NATIVE / "candidates").mkdir()
    records = []
    for case, relative_model, taps, multiple, mutation in CASES:
        model = (HERE / relative_model).resolve()
        witness = NATIVE / "candidates" / (case + ".aag")
        command = [sys.executable, "-m", "research.odd_order_witness_v1.produce", "--model", str(model),
                   "--taps", hex(taps), "--odd-multiple", str(multiple), "--output", str(witness)]
        if mutation:
            command += ["--mutation", mutation]
        started = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=10)
        elapsed = time.perf_counter() - started
        (NATIVE / "candidates" / (case + ".stdout.txt")).write_bytes(result.stdout)
        (NATIVE / "candidates" / (case + ".stderr.txt")).write_bytes(result.stderr)
        require(result.returncode == 0, "Candidate construction failed: " + case)
        metadata = json.loads(result.stdout)
        records.append({"case": case, "command": command, "returncode": result.returncode,
                        "elapsed_seconds": elapsed, "model_path": str(model), "model_sha256": sha(model),
                        "witness_path": str(witness), "witness_sha256": sha(witness),
                        "witness_bytes": witness.stat().st_size, "metadata": metadata})
    construction = {"timing_scope": "One fresh Python process per candidate before native replay; includes imports, factorization, algebra, AAG construction and file output. Excludes model emission and native verification.",
                    "cases": records}
    (NATIVE / "CONSTRUCTION.json").write_text(json.dumps(construction, indent=2) + "\n")
    source_paths = ["research/odd_order_witness_v1/run_native.py", "research/odd_order_witness_v1/produce.py",
                    "research/odd_order_witness_v1/model_controls.py", "research/proof_interface_v1/run_native.py",
                    "research/proof_interface_v1/produce.py", "research/aiger_lfsr_v1/check.py"]
    provenance = {"protocol_sha256": sha(HERE / "NATIVE_PROTOCOL.md"),
                  "source_files_sha256": {path: sha(ROOT / path) for path in source_paths},
                  "binary_sha256": old["binary_sha256"],
                  "source_pins": {"certifaiger": "27d526e3e979074c3e92582768f577dc6eddb0da",
                                  "aiger": "039ec1a2cc37d3093ac35c4b6df65336b346f409",
                                  "cadical": "c60730422e758ef1cebe7aeddf2dda31c996bf04",
                                  "lrat-trim": "adba6e61368e91957c79bf952b29800f05dbee51"},
                  "reused_driver": "research/proof_interface_v1/run_native.py",
                  "environment_record": "research/proof_interface_v1/native/BUILD_PROVENANCE.json",
                  "construction_sha256": sha(NATIVE / "CONSTRUCTION.json")}
    (NATIVE / "BUILD_PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"prepared": [r["case"] for r in records], "construction_seconds": [r["elapsed_seconds"] for r in records]}))


def execute(tools):
    provenance = json.loads((NATIVE / "BUILD_PROVENANCE.json").read_text())
    construction = json.loads((NATIVE / "CONSTRUCTION.json").read_text())
    require(sha(HERE / "NATIVE_PROTOCOL.md") == provenance["protocol_sha256"], "Frozen protocol changed")
    require(sha(NATIVE / "CONSTRUCTION.json") == provenance["construction_sha256"], "Construction freeze changed")
    for path, expected in provenance["source_files_sha256"].items():
        require(sha(ROOT / path) == expected, "Frozen constructor/driver changed: " + path)
    for name, expected in provenance["binary_sha256"].items():
        require(sha(tools / name) == expected, "Frozen tool changed: " + name)
    require([r["case"] for r in construction["cases"]] == [r[0] for r in CASES], "Frozen case set changed")
    for record in construction["cases"]:
        case = record["case"]
        model, witness = Path(record["model_path"]), Path(record["witness_path"])
        require(sha(model) == record["model_sha256"] and sha(witness) == record["witness_sha256"], "Frozen candidate changed")
        require(not (NATIVE / case).exists(), "Refusing to repeat native case: " + case)
    for record in construction["cases"]:
        case = record["case"]
        command = [sys.executable, str(DRIVER), "--tools", str(tools), "--model", record["model_path"],
                   "--witness", record["witness_path"], "--output", str(NATIVE / case)]
        with (NATIVE / (case + "_driver.stdout.txt")).open("xb") as out, (NATIVE / (case + "_driver.stderr.txt")).open("xb") as err:
            completed = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
        require(completed.returncode == 0, "Native orchestration error; preserve existing evidence")
        result = json.loads((NATIVE / case / "RESULTS.json").read_text())
        print(json.dumps({"case": case, "status": result["status"], "reason": result.get("reason"),
                          "elapsed_seconds": result["elapsed_seconds"], "artifact_bytes": result["artifact_bytes"]}), flush=True)
    artifacts = {}
    for case, *_ in CASES:
        for path in sorted((NATIVE / case).iterdir()):
            require(path.is_file(), "Unexpected case subdirectory")
            raw = path.read_bytes()
            logical = str(path.relative_to(NATIVE))
            if len(raw) > 65536:
                stored = path.with_name(path.name + ".gz")
                require(not stored.exists(), "Refusing to overwrite compressed evidence")
                payload = gzip.compress(raw, mtime=0)
                stored.write_bytes(payload)
                path.unlink()
                encoding = "gzip"
            else:
                stored, payload, encoding = path, raw, "raw"
            artifacts[logical] = {"stored_path": str(stored.relative_to(NATIVE)), "encoding": encoding,
                                  "raw_bytes": len(raw), "raw_sha256": hashlib.sha256(raw).hexdigest(),
                                  "stored_bytes": len(payload), "stored_sha256": hashlib.sha256(payload).hexdigest()}
    (NATIVE / "ARTIFACTS.json").write_text(json.dumps(artifacts, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "execute"))
    parser.add_argument("--tools", required=True, type=Path)
    args = parser.parse_args()
    (prepare if args.mode == "prepare" else execute)(args.tools.resolve())
