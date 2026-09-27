"""Replay the bounded conceptual audit without external dependencies."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / "MANIFEST.json").read_text())
    for name, expected in manifest["sha256"].items():
        if hashlib.sha256((here / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Invariant/history checkpoint changed: " + name)
    subprocess.run([sys.executable, "-m", "research.invariant_history_v1.verify_controls"],
                   cwd=here.parents[1], check=True)
    print("PASS: bounded invariant/history characterization and premise controls.")
    print("The inverse-bit separator mechanism has a direct predecessor; no novelty or size lower bound is certified.")


if __name__ == "__main__":
    main()
