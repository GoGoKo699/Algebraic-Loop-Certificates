"""Offline integrity and conversion replay of the recorded native experiment."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_native():
    module = Path(__file__).resolve().parent
    base = module / "native"
    manifest = json.loads((base / "MANIFEST.json").read_text())
    for entry in manifest["files"]:
        path = module / entry["path"]
        require(path.is_file(), f"Missing evidence: {entry['path']}")
        require(digest(path) == entry["sha256"], f"Evidence changed: {entry['path']}")
    observed = json.loads((base / "results/results.json").read_text())
    require(digest(module / "run_native.py") == observed["runner_sha256"], "Observed runner changed")
    require(digest(base / "PLAN.json") == observed["plan_sha256"], "Observed plan changed")
    tool = json.loads((base / "TOOL_PROVENANCE.json").read_text())
    require(tool["abc"]["binary_sha256"] == observed["abc_binary_sha256"], "ABC binary provenance mismatch")
    require(tool["aigtoaig"]["binary_sha256"] == observed["aigtoaig_binary_sha256"], "AIGER binary provenance mismatch")
    require(tool["abc"]["commit"] == "ab2139ee0c418f54136deb4e8e89eeea3b87efc8", "ABC source pin mismatch")
    require(tool["aigtoaig"]["commit"] == "039ec1a2cc37d3093ac35c4b6df65336b346f409", "AIGER source pin mismatch")
    spec = importlib.util.spec_from_file_location("observed_native_runner", module / "run_native.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    require([c["n"] for c in observed["results"]] == [2, 4, 8, 12, 16, 24], "Fixed subset changed")
    upstream = json.loads((module / "SOURCE_MANIFEST.json").read_text())
    require(upstream["commit"] == "c8efd0251c0548dd46168db8410e6777c5f82b73", "Corpus pin mismatch")
    blobs = {r["file"]: r["git_blob_sha1"] for r in upstream["files"]}
    for case in observed["results"]:
        n = case["n"]
        source = module / "upstream" / case["input_filename"]
        binary = base / "results" / case["binary_filename"]
        roundtrip = base / "results" / case["input_filename"]
        raw = source.read_bytes()
        gitblob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        require(gitblob == blobs[source.name], f"Source Git blob mismatch: n={n}")
        require(digest(source) == case["input_sha256"], f"Source SHA256 mismatch: n={n}")
        require(digest(binary) == case["binary_sha256"], f"Converted AIGER mismatch: n={n}")
        require(digest(roundtrip) == case["roundtrip_sha256"], f"Roundtrip AIGER mismatch: n={n}")
        require(runner.same_transition_structure(source, roundtrip), f"Transition structure mismatch: n={n}")
        stdout = (base / "results" / f"n{n:02d}.stdout").read_text()
        timing = json.loads((base / "results" / f"n{n:02d}-time.json").read_text())
        require(timing["wall_seconds"] == case["wall_seconds_including_wrapper"], f"Timing mismatch: n={n}")
        if n in (2, 4):
            require(case["status"] == "solver_reported_safe" and case["returncode"] == 0, f"Safe status mismatch: n={n}")
            require(re.search(r"^Status = 1\s", stdout, re.M) is not None, f"Missing native safe status: n={n}")
            require(not timing["timeout_killed_by_harness"], f"Unexpected timeout: n={n}")
        else:
            require(case["status"] == "wall_timeout_unknown" and case["returncode"] == -9, f"Unknown status mismatch: n={n}")
            require(timing["timeout_killed_by_harness"] and timing["wall_seconds"] >= 10, f"Timeout evidence missing: n={n}")
    return {"cases": 6, "native_safe": 2, "native_unknown": 4, "conversion_structures_equal": 6}


if __name__ == "__main__":
    print(json.dumps(verify_native(), sort_keys=True))
