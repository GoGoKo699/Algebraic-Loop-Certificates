"""Portable replay of the odd-order witness checkpoint; no native solver runs."""

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
        if hashlib.sha256((here / relative).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Odd-order witness checkpoint changed: " + relative)
    for module in ("model_controls", "verify_theory", "verify_producer", "verify_native"):
        subprocess.run([sys.executable, "-m", "research.odd_order_witness_v1." + module],
                       cwd=root, check=True)
    print("PASS: odd-order witness checkpoint, source controls and retained proof replay.")
    print("Factoring the exponent is construction work; native source-to-CNF translation remains trusted.")


if __name__ == "__main__":
    main()
