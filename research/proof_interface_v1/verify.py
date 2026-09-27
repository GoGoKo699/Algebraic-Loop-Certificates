"""Replay this research checkpoint without downloading or starting native tools."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    manifest = json.loads((here / "MANIFEST.json").read_text())
    for relative, expected in manifest["sha256"].items():
        path = here / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("Proof-interface checkpoint changed: " + relative)
    for module in ("verify_theory", "verify_producer", "verify_lrat", "verify_native"):
        subprocess.run([sys.executable, "-m", "research.proof_interface_v1." + module],
                       cwd=root, check=True)
    print("PASS: preserved proof-interface checkpoint and independent offline checks.")
    print("CNF proof replay does not independently certify native obligation/CNF translation.")


if __name__ == "__main__":
    main()
